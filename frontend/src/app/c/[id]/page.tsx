"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { ChatInput } from "@/components/conversation/ChatInput";
import { MessageList } from "@/components/conversation/MessageList";
import { ThemeToggle } from "@/components/ThemeToggle";
import { useConversation } from "@/hooks/useConversation";

interface ConversationPageProps {
  params: Promise<{ id: string }>;
}

export default function ConversationPage({ params }: ConversationPageProps) {
  const router = useRouter();
  const [convId, setConvId] = useState<string | null>(null);

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
      <div className="flex flex-col min-h-screen bg-lk-bg">
        <header className="border-b border-lk-border py-3 bg-lk-card">
          <div className="lk-shell flex items-center justify-between">
            <button
              className="lk-btn lk-btn-sm lk-btn-ghost"
              onClick={handleBack}
            >
              ← Feed
            </button>
            <ThemeToggle />
          </div>
        </header>
        <main className="flex-1 lk-shell py-8">
          <div className="animate-pulse space-y-4">
            <div className="h-4 bg-lk-muted/20 rounded w-1/3" />
            <div className="h-16 bg-lk-muted/20 rounded-md w-3/4" />
            <div className="h-16 bg-lk-muted/20 rounded-md w-1/2 ml-auto" />
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="flex flex-col min-h-screen bg-lk-bg">
      {/* Header: back button + title */}
      <header className="border-b border-lk-border py-3.5 bg-lk-card sticky top-0 z-20 shadow-xs">
        <div className="lk-shell flex items-center justify-between gap-4">
          <div className="flex items-center gap-3 truncate">
            <button
              className="lk-btn lk-btn-sm lk-btn-ghost shrink-0"
              onClick={handleBack}
            >
              ← Feed
            </button>
            <h1 className="text-sm font-semibold text-lk-fg truncate">
              {conversation?.title || "Conversation"}
            </h1>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            {conversation?.seed_kind === "card" && conversation.seed_ref && (
              <span className="lk-badge text-lk-secondary bg-lk-secondary/10 shrink-0">
                Card seed
              </span>
            )}
            <ThemeToggle />
          </div>
        </div>
      </header>

      {/* Message list */}
      <main className="flex-1 pb-4">
        {error && (
          <div className="lk-shell mt-4">
            <div className="p-3 text-sm text-lk-primary bg-lk-primary/10 border border-lk-primary/20 rounded-md">
              {error}
            </div>
          </div>
        )}
        <MessageList messages={messages} />
      </main>

      {/* Input */}
      <ChatInput onSend={handleSend} disabled={sending} />
    </div>
  );
}
