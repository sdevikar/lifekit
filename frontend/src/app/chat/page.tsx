"use client";

import { useState } from "react";
import { MasterComposer } from "@/components/feed/MasterComposer";
import { ChatView } from "@/components/ChatView";
import { useConversations } from "@/hooks/useConversations";
import { apiPost } from "@/types/api";

export default function ChatPage() {
  const { conversations, refresh } = useConversations();
  const [selectedConvId, setSelectedConvId] = useState<string | null>(null);
  const [initialMessage, setInitialMessage] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);

  const handleComposerSubmit = async (text: string) => {
    setCreating(true);
    try {
      const resp = await apiPost<{ id: string }>("/api/conversations", {
        seed_kind: "composer",
        title: text,
      });
      // Show the chat view immediately; the first message is sent after mount
      // so the optimistic update is visible while the LLM generates.
      setInitialMessage(text);
      setSelectedConvId(resp.id);
      refresh();
    } catch {
      // TODO: surface error
    } finally {
      setCreating(false);
    }
  };

  if (selectedConvId) {
    return (
      <ChatView
        convId={selectedConvId}
        initialMessage={initialMessage ?? undefined}
      />
    );
  }

  return (
    <div className="flex flex-col min-h-screen bg-lk-bg">
      <header className="border-b border-lk-border py-3.5 bg-lk-card sticky top-0 z-20 shadow-xs">
        <div className="lk-shell flex items-center justify-between gap-4">
          <h1 className="text-sm font-semibold text-lk-fg">Chat</h1>
        </div>
      </header>

      <main className="flex-1 flex items-center justify-center p-8">
        <p className="text-sm text-lk-muted">
          Start a conversation or pick one from the sidebar.
        </p>
      </main>

      <MasterComposer
        onSubmit={handleComposerSubmit}
        submitting={creating}
      />
    </div>
  );
}
