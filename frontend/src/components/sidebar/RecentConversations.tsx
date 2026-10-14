"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useConversations } from "@/hooks/useConversations";
import { apiPatch, apiDelete, apiPost } from "@/types/api";

function getDayGroup(dateStr: string): string {
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  if (diffDays === 0) return "Today";
  if (diffDays === 1) return "Yesterday";
  if (diffDays < 7) return "Last 7 days";
  return "Earlier";
}

const GROUP_ORDER = ["Today", "Yesterday", "Last 7 days", "Earlier"];

export function RecentConversations() {
  const router = useRouter();
  const { conversations, loading, error, refresh } = useConversations();
  const [collapsed, setCollapsed] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState("");

  const handleSelect = (id: string) => {
    router.push(`/chat/${id}`);
  };

  const handleRename = async (id: string) => {
    const title = editTitle.trim();
    if (!title) {
      setEditingId(null);
      return;
    }
    await apiPatch(`/api/conversations/${id}`, { title });
    setEditingId(null);
    refresh();
  };

  const handleDelete = async (id: string) => {
    await apiDelete(`/api/conversations/${id}`);
    refresh();
  };

  if (loading) {
    return (
      <div className="px-3 py-2 space-y-2">
        <div className="h-4 bg-lk-muted/20 rounded w-1/2 animate-pulse" />
        <div className="h-4 bg-lk-muted/20 rounded w-3/4 animate-pulse" />
      </div>
    );
  }

  if (error) {
    return <p className="px-3 py-2 text-xs text-lk-primary">{error}</p>;
  }

  const groups: Record<string, typeof conversations> = {};
  for (const conv of conversations) {
    const group = getDayGroup(conv.updated_at);
    if (!groups[group]) groups[group] = [];
    groups[group].push(conv);
  }

  return (
    <div className="px-2 py-1">
      <button
        type="button"
        onClick={() => setCollapsed(!collapsed)}
        className="flex items-center gap-1.5 w-full px-2 py-1.5 text-xs font-semibold uppercase tracking-wider text-lk-muted hover:text-lk-fg transition-colors"
      >
        <svg
          width="12"
          height="12"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          className={`transition-transform ${collapsed ? "" : "rotate-90"}`}
        >
          <polyline points="9 18 15 12 9 6" />
        </svg>
        Recent
      </button>

      {!collapsed && (
        <div className="space-y-2">
          <button
            type="button"
            onClick={() => router.push("/chat")}
            className="flex items-center gap-2 w-full px-2 py-1.5 rounded-md text-xs text-lk-muted hover:text-lk-fg hover:bg-lk-user-msg transition-colors"
            aria-label="New chat"
          >
            <svg
              width="12"
              height="12"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              aria-hidden="true"
            >
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
              <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
            </svg>
            <span>New chat</span>
          </button>
          {GROUP_ORDER.filter((g) => groups[g]).map((group) => (
            <div key={group}>
              <div className="px-2 py-1 text-[10px] font-semibold uppercase tracking-wider text-lk-muted/70">
                {group}
              </div>
              <ul className="space-y-0.5">
                {groups[group].map((conv) => (
                  <li key={conv.id} className="group relative">
                    {editingId === conv.id ? (
                      <div className="flex items-center gap-1 px-2 py-1">
                        <input
                          type="text"
                          value={editTitle}
                          onChange={(e) => setEditTitle(e.target.value)}
                          onKeyDown={(e) => {
                            if (e.key === "Enter") handleRename(conv.id);
                            if (e.key === "Escape") setEditingId(null);
                          }}
                          className="flex-1 min-w-0 px-1.5 py-0.5 text-xs rounded border border-lk-border bg-lk-bg text-lk-fg outline-none focus:ring-1 focus:ring-lk-primary/40"
                          autoFocus
                        />
                      </div>
                    ) : (
                      <div
                        role="button"
                        tabIndex={0}
                        onClick={() => handleSelect(conv.id)}
                        onKeyDown={(e) => {
                          if (e.key === "Enter" || e.key === " ") {
                            e.preventDefault();
                            handleSelect(conv.id);
                          }
                        }}
                        className="flex items-center gap-2 px-2 py-1.5 rounded-md text-xs text-lk-fg hover:bg-lk-user-msg cursor-pointer transition-colors"
                      >
                        <span className="truncate flex-1">{conv.title}</span>
                        <div className="hidden group-hover:flex items-center gap-0.5 shrink-0">
                          <button
                            type="button"
                            onClick={(e) => {
                              e.stopPropagation();
                              setEditingId(conv.id);
                              setEditTitle(conv.title);
                            }}
                            className="p-0.5 rounded text-lk-muted hover:text-lk-fg"
                            aria-label="Rename"
                          >
                            <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                              <path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z" />
                            </svg>
                          </button>
                          <button
                            type="button"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleDelete(conv.id);
                            }}
                            className="p-0.5 rounded text-lk-muted hover:text-lk-primary"
                            aria-label="Delete"
                          >
                            <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                              <path d="M3 6h18" />
                              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6" />
                              <path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                            </svg>
                          </button>
                        </div>
                      </div>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
