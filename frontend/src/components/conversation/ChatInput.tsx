"use client";

import { useState } from "react";
import { SendIcon } from "@/components/feed/icons";

interface ChatInputProps {
  onSend: (text: string) => Promise<void>;
  disabled?: boolean;
}

export function ChatInput({ onSend, disabled = false }: ChatInputProps) {
  const [text, setText] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = text.trim();
    if (!trimmed || disabled) return;
    setText("");
    try {
      await onSend(trimmed);
    } catch {
      setText(trimmed);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="p-4 border-t border-lk-border bg-lk-bg/95 backdrop-blur-sm sticky bottom-0 z-10"
    >
      <div className="lk-shell flex gap-2">
        <input
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Ask your coach a question…"
          className="lk-input flex-1"
          disabled={disabled}
          maxLength={1000}
          autoFocus
        />
        <button
          type="submit"
          disabled={!text.trim() || disabled}
          className="lk-btn"
        >
          {disabled ? "Sending…" : <SendIcon />}
        </button>
      </div>
    </form>
  );
}
