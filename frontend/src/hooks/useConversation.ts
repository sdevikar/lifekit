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

    // The coach bubble is created lazily on the first delta so the pending
    // "thinking" indicator shows alone until text starts streaming — avoids
    // a duplicate empty coach bubble next to the balls.
    const coachMsg: Message = {
      role: "coach",
      text: "",
      created_at: new Date().toISOString(),
    };
    const coachMsgRef = { current: coachMsg };

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
              const last = next[next.length - 1];
              if (last && last.role === "coach") {
                next[next.length - 1] = { ...last, text: last.text + payload.delta! };
              } else {
                const created = { ...coachMsg, text: payload.delta! };
                coachMsgRef.current = created;
                next.push(created);
              }
              return next;
            });
          }
          if (payload.done) {
            finalReply = payload.reply ?? "";
          }
        }
      }
      // Replace the streaming coach message with the final parsed reply.
      setMessages((prev) => {
        const next = [...prev];
        const last = next[next.length - 1];
        if (last && last.role === "coach") {
          next[next.length - 1] = { ...last, text: finalReply || last.text };
        } else if (finalReply) {
          next.push({ ...coachMsg, text: finalReply });
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
      setMessages((prev) => prev.filter((m) => m !== optimistic && m !== coachMsgRef.current));
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