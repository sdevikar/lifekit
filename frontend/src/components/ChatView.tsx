"use client";

import { useEffect, useRef, useState } from "react";
import { useConversation } from "@/hooks/useConversation";
import { MessageList } from "./conversation/MessageList";
import { ChatInput } from "./conversation/ChatInput";
import { apiPatch } from "@/types/api";

interface ChatViewProps {
  convId: string;
  initialMessage?: string;
}

export function ChatView({ convId, initialMessage }: ChatViewProps) {
  const { conversation, messages, loading, sending, error, sendMessage, stop, refresh } =
    useConversation(convId);
  const sentInitialRef = useRef(false);

  // Send the composer's first message after the conversation has loaded, so
  // the optimistic user bubble shows immediately while the LLM generates.
  useEffect(() => {
    if (loading || sentInitialRef.current || !initialMessage || messages.length > 0) return;
    sentInitialRef.current = true;
    void sendMessage(initialMessage);
  }, [loading, initialMessage, messages.length, sendMessage]);
  const [editing, setEditing] = useState(false);
  const [titleDraft, setTitleDraft] = useState("");
  const [saving, setSaving] = useState(false);
  const [renameError, setRenameError] = useState<string | null>(null);
  const committingRef = useRef(false);
  const cancellingRef = useRef(false);
  const editingRef = useRef(editing);
  const syncEditingRef = (v: boolean) => {
    editingRef.current = v;
    setEditing(v);
  };

  const startEdit = () => {
    if (saving) return;
    setTitleDraft(conversation?.title ?? "");
    setRenameError(null);
    syncEditingRef(true);
  };

  const cancelEdit = () => {
    syncEditingRef(false);
    setRenameError(null);
  };

  const commitEdit = async () => {
    if (!editingRef.current) return;
    if (committingRef.current) return;
    const title = titleDraft.trim();
    if (!title) {
      cancelEdit();
      return;
    }
    if (title === conversation?.title) {
      cancelEdit();
      return;
    }
    committingRef.current = true;
    setSaving(true);
    setRenameError(null);
    try {
      await apiPatch(`/api/conversations/${convId}`, { title });
      await refresh();
    } catch (err) {
      setRenameError(err instanceof Error ? err.message : "Failed to rename");
      setSaving(false);
      committingRef.current = false;
      return;
    }
    setSaving(false);
    committingRef.current = false;
    syncEditingRef(false);
  };

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="animate-pulse space-y-3 w-full max-w-md px-4">
          <div className="h-4 bg-lk-muted/20 rounded w-1/3" />
          <div className="h-4 bg-lk-muted/20 rounded w-2/3" />
          <div className="h-4 bg-lk-muted/20 rounded w-1/2" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex-1 flex items-center justify-center p-8">
        <p className="text-sm text-lk-primary">{error}</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      <header className="border-b border-lk-border py-3.5 bg-lk-card shrink-0">
        <div className="lk-shell">
          {editing ? (
            <div className="flex flex-col gap-1">
              <input
                type="text"
                value={titleDraft}
                onChange={(e) => setTitleDraft(e.target.value)}
                onBlur={() => {
                  if (cancellingRef.current) {
                    cancellingRef.current = false;
                    return;
                  }
                  void commitEdit();
                }}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    e.preventDefault();
                    void commitEdit();
                  }
                  if (e.key === "Escape") {
                    cancellingRef.current = true;
                    cancelEdit();
                  }
                }}
                className="w-full px-2 py-1 text-sm font-semibold rounded border border-lk-border bg-lk-bg text-lk-fg outline-none focus:ring-1 focus:ring-lk-primary/40"
                autoFocus
                disabled={saving}
              />
              <div className="flex items-center gap-2 text-xs">
                {saving && <span className="text-lk-muted">Saving…</span>}
                {renameError && <span className="text-lk-primary">{renameError}</span>}
              </div>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={startEdit}
                className="text-sm font-semibold text-lk-fg hover:text-lk-primary transition-colors"
              >
                {conversation?.title ?? "Conversation"}
              </button>
              {saving && <span className="text-xs text-lk-muted">Saving…</span>}
            </div>
          )}
        </div>
      </header>

      <div className="flex-1 overflow-y-auto">
        <MessageList
          messages={messages}
          pending={
            sending ||
            (messages.length > 0 &&
              messages[messages.length - 1].role === "user")
          }
        />
      </div>

      <ChatInput
        onSend={async (text) => {
          await sendMessage(text);
        }}
        onStop={stop}
        disabled={sending}
      />
    </div>
  );
}
