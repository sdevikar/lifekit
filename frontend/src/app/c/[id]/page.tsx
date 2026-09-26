"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { ChatInput } from "@/components/conversation/ChatInput";
import { MessageList } from "@/components/conversation/MessageList";
import { useConversation } from "@/hooks/useConversation";

interface ConversationPageProps {
  params: Promise<{ id: string }>;
}

export default function ConversationPage({ params }: ConversationPageProps) {
  const router = useRouter();
  const [convId, setConvId] = useState<string | null>(null);

  // Resolve params (async in App Router)
  useEffect(() => {
    params.then((p) => setConvId(p.id));
  }, [params]);

  const { conversation, messages, loading, sending, error, sendMessage } =
    useConversation(convId || "");

  const handleSend = async (text: string) => {
    if (!convId) return;
    await sendMessage(text);
  };

  const handleBack = () => {
    router.push("/feed");
  };

  if (loading || !convId) {
    return (
      <div className="flex flex-col h-screen">
        <header className="border-b border-lk-border p-4">
          <button
            className="lk-btn lk-btn-sm lk-btn-secondary"
            onClick={handleBack}
          >
            ← Feed
          </button>
        </header>
        <main className="flex-1 p-4 overflow-y-auto">
          <div className="animate-pulse space-y-3">
            <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4" />
            <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2" />
            <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-full" />
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen">
      {/* Header: back button + title */}
      <header className="border-b border-lk-border p-4 bg-lk-bg">
        <div className="max-w-2xl mx-auto flex items-center gap-3">
          <button
            className="lk-btn lk-btn-sm lk-btn-secondary"
            onClick={handleBack}
          >
            ← Feed
          </button>
          <h1 className="text-lg font-semibold truncate">
            {conversation?.title || "Conversation"}
          </h1>
        </div>

        {/* Seed context display */}
        {conversation?.seed_kind === "card" && conversation.seed_ref && (
          <div className="max-w-2xl mx-auto mt-2 px-4">
            <span className="lk-badge bg-lk-accent/10 text-lk-accent">
              Seeded from card
            </span>
          </div>
        )}
      </header>

      {/* Message list */}
      <main className="flex-1 overflow-y-auto">
        {error && (
          <div className="p-3 mx-3 mt-2 text-sm text-red-500 bg-red-50 dark:bg-red-900/20 rounded-md">
            {error}
          </div>
        )}
        <MessageList messages={messages} />
      </main>

      {/* Input */}
      <ChatInput onSend={handleSend} disabled={sending} />
    </div>
  );
}