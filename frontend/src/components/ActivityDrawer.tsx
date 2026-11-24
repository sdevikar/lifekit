"use client";

import { useEffect, useState } from "react";
import { ChatView } from "./ChatView";
import { apiPost } from "@/types/api";

export type DrawerCard = {
  kind: "exercise" | "idea" | "resurfaced";
  id: number;
  title: string;
  text: string;
};

interface ActivityDrawerProps {
  card: DrawerCard | null;
  onClose: () => void;
  onMarkDone?: (exerciseId: number) => Promise<void>;
  markingDone?: boolean;
}

export function ActivityDrawer({
  card,
  onClose,
  onMarkDone,
  markingDone,
}: ActivityDrawerProps) {
  const [convId, setConvId] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!card) {
      setConvId(null);
      return;
    }
    let cancelled = false;
    setCreating(true);
    setError(null);
    setConvId(null);
    apiPost<{ id: string }>("/api/conversations", {
      seed_kind: "card",
      seed_ref: `${card.kind}:${card.id}`,
      title: card.title || card.text.slice(0, 60),
    })
      .then((resp) => {
        if (!cancelled) setConvId(resp.id);
      })
      .catch((e) => {
        if (!cancelled) setError(e instanceof Error ? e.message : "Failed");
      })
      .finally(() => {
        if (!cancelled) setCreating(false);
      });
    return () => {
      cancelled = true;
    };
  }, [card]);

  if (!card) return null;

  return (
    <>
      <div
        className="fixed inset-0 bg-black/30 z-30"
        onClick={onClose}
        aria-hidden="true"
      />
      <aside className="fixed top-0 right-0 h-full w-full sm:w-[440px] bg-lk-bg border-l border-lk-border shadow-panel z-40 flex flex-col">
        <header className="flex items-center justify-between gap-2 px-4 py-3 border-b border-lk-border shrink-0">
          <h2 className="text-sm font-semibold text-lk-fg truncate">
            {card.title || "Card"}
          </h2>
          <button
            type="button"
            onClick={onClose}
            className="lk-btn lk-btn-sm lk-btn-ghost px-2"
            aria-label="Close"
          >
            ✕
          </button>
        </header>
        <div className="px-4 py-3 border-b border-lk-border shrink-0">
          <p className="text-sm text-lk-fg">{card.text}</p>
          {card.kind === "exercise" && onMarkDone && (
            <button
              type="button"
              onClick={() => onMarkDone(card.id)}
              disabled={markingDone}
              className="lk-btn lk-btn-sm mt-3"
            >
              {markingDone ? "Saving…" : "Mark done"}
            </button>
          )}
        </div>
        <div className="flex-1 min-h-0">
          {creating && (
            <div className="flex items-center justify-center h-full text-sm text-lk-muted">
              Opening…
            </div>
          )}
          {error && (
            <div className="flex items-center justify-center h-full text-sm text-lk-primary">
              {error}
            </div>
          )}
          {convId && <ChatView convId={convId} />}
        </div>
      </aside>
    </>
  );
}