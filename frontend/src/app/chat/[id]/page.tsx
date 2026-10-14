"use client";

import { useEffect, useState } from "react";
import { ChatView } from "@/components/ChatView";

interface ChatSessionPageProps {
  params: Promise<{ id: string }>;
}

export default function ChatSessionPage({ params }: ChatSessionPageProps) {
  const [convId, setConvId] = useState<string | null>(null);

  useEffect(() => {
    params.then((p) => setConvId(p.id));
  }, [params]);

  if (!convId) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="animate-pulse space-y-3 w-full max-w-md px-4">
          <div className="h-4 bg-lk-muted/20 rounded w-1/3" />
          <div className="h-4 bg-lk-muted/20 rounded w-2/3" />
        </div>
      </div>
    );
  }

  return <ChatView convId={convId} />;
}
