import { useCallback, useEffect, useRef, useState } from "react";
import {
  ConversationResponse,
  ConversationDetail,
  Message,
  apiGet,
  apiPost,
} from "@/types/api";

export function useConversation(convId: string) {
  const [conversation, setConversation] = useState<ConversationDetail | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const load = useCallback(async () => {
    // No id yet (route params are async) — fetching would hit the
    // /api/conversations/ collection, which returns an array, not a
    // conversation, and crashes MessageList on `messages.length`.
    if (!convId) return;
    setLoading(true);
    setError(null);
    try {
      const resp = await apiGet<ConversationResponse>(
        `/api/conversations/${convId}`,
      );
      setConversation(resp.conversation);
      setMessages(resp.messages);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load conversation");
    } finally {
      setLoading(false);
    }
  }, [convId]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    load();
  }, [load]);

  const sendMessage = async (text: string) => {
    if (sending) return;
    setSending(true);
    setError(null);

    const controller = new AbortController();
    abortRef.current = controller;

    // Append the user's message now, not after the await. The local model
    // takes tens of seconds and an input that clears itself with no visible
    // change reads as a hang. Filtered by object identity on rollback below —
    // Message carries no id, so there is nothing else to match on.
    const optimistic: Message = {
      role: "user",
      text,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, optimistic]);

    // Streaming coach reply: read SSE deltas and append a live coach message.
    const streamingMsg: Message = {
      role: "coach",
      text: "",
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, streamingMsg]);

    try {
      const res = await fetch(`/api/conversations/${convId}/messages`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
        signal: controller.signal,
      });
      if (!res.ok || !res.body) {
        throw new Error(`Coach unavailable (${res.status})`);
      }
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      let finalReply = "";
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() ?? "";
        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed.startsWith("data:")) continue;
          let payload: { delta?: string; done?: boolean; reply?: string; error?: string };
          try {
            payload = JSON.parse(trimmed.slice(5).trim());
          } catch {
            continue;
          }
          if (payload.error) throw new Error(payload.error);
          if (payload.delta) {
            setMessages((prev) => {
              const next = [...prev];
              const idx = next.lastIndexOf(streamingMsg);
              // fall back to last coach message
              const target = idx >= 0 ? idx : next.length - 1;
              if (target >= 0 && next[target]?.role === "coach") {
                next[target] = { ...next[target], text: next[target].text + payload.delta! };
              }
              return next;
            });
          }
          if (payload.done) {
            finalReply = payload.reply ?? "";
          }
        }
      }
      // Replace streaming message with final parsed reply.
      setMessages((prev) => {
        const next = [...prev];
        const idx = next.findIndex((m) => m === streamingMsg);
        const target = idx >= 0 ? idx : next.length - 1;
        if (target >= 0 && next[target]?.role === "coach") {
          next[target] = { ...next[target], text: finalReply || next[target].text };
        }
        return next;
      });
      return finalReply;
    } catch (err) {
      if (controller.signal.aborted) {
        // User interrupted: keep the user's message, drop nothing else.
        setError(null);
        return;
      }
      // The server replies before it persists, so a failure means nothing was
      // stored. Drop the optimistic message — the transcript must match the DB.
      setMessages((prev) => prev.filter((m) => m !== optimistic && m !== streamingMsg));
      setError(err instanceof Error ? err.message : "Failed to send message");
      throw err;
    } finally {
      abortRef.current = null;
      setSending(false);
    }
  };

  const stop = useCallback(() => {
    abortRef.current?.abort();
  }, []);

  return {
    conversation,
    messages,
    loading,
    sending,
    error,
    sendMessage,
    stop,
    refresh: load,
  };
}