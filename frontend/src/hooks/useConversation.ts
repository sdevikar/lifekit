import { useCallback, useEffect, useState } from "react";
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
    load();
  }, [load]);

  const sendMessage = async (text: string) => {
    if (sending) return;
    setSending(true);
    setError(null);

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

    try {
      const resp = await apiPost<{ reply: string }>(
        `/api/conversations/${convId}/messages`,
        { text },
      );
      setMessages((prev) => [
        ...prev,
        { role: "coach", text: resp.reply, created_at: new Date().toISOString() },
      ]);
      return resp.reply;
    } catch (err) {
      // The server replies before it persists, so a failure means nothing was
      // stored. Drop the optimistic message — the transcript must match the DB.
      setMessages((prev) => prev.filter((m) => m !== optimistic));
      setError(err instanceof Error ? err.message : "Failed to send message");
      throw err;
    } finally {
      setSending(false);
    }
  };

  return {
    conversation,
    messages,
    loading,
    sending,
    error,
    sendMessage,
    refresh: load,
  };
}