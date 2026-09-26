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
    setSending(true);
    setError(null);
    try {
      const resp = await apiPost<{ reply: string }>(
        `/api/conversations/${convId}/messages`,
        { text },
      );

      // Optimistically add the user message + coach reply
      const now = new Date().toISOString();
      setMessages((prev) => [
        ...prev,
        { role: "user", text, created_at: now },
        { role: "coach", text: resp.reply, created_at: now },
      ]);

      return resp.reply;
    } catch (err) {
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