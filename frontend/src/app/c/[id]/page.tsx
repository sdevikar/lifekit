"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

interface ConversationPageProps {
  params: Promise<{ id: string }>;
}

export default function ConversationPage({ params }: ConversationPageProps) {
  const router = useRouter();

  useEffect(() => {
    params.then((p) => {
      router.replace(`/chat/${p.id}`);
    });
  }, [params, router]);

  return (
    <div className="flex flex-col min-h-screen bg-lk-bg">
      <main className="flex-1 flex items-center justify-center">
        <p className="text-sm text-lk-muted">Redirecting…</p>
      </main>
    </div>
  );
}
