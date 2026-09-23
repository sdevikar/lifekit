"use client";

import { useRouter } from "next/navigation";

interface ConversationPageProps {
  params: Promise<{ id: string }>;
}

// Stub page for Step 13b — full conversation view comes in Step 13c.
// For now: back to feed + placeholder.
export default async function ConversationPage({ params }: ConversationPageProps) {
  const { id } = await params;
  const router = useRouter();

  return (
    <div className="flex flex-col h-screen pb-24">
      {/* Header with back button */}
      <header className="border-b border-lk-border p-4">
        <button
          className="lk-btn lk-btn-sm lk-btn-secondary"
          onClick={() => router.push("/feed")}
        >
          ← Feed
        </button>
      </header>

      <main className="flex-1 p-4 overflow-y-auto">
        <p className="text-lk-muted">
          Conversation <code>{id}</code> — full view coming in Step 13c.
        </p>
      </main>
    </div>
  );
}