"use client";

import { useState } from "react";
import { SendIcon } from "@/components/feed/icons";

interface ChatInputProps {
  onSend: (text: string) => Promise<void>;
  onStop?: () => void;
  disabled?: boolean;
}

export function ChatInput({ onSend, onStop, disabled = false }: ChatInputProps) {
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
          placeholder={
            disabled ? "Coach is thinking…" : "Ask your coach a question…"
          }
          className="lk-input flex-1"
          disabled={disabled}
          maxLength={1000}
        />
        {disabled ? (
          <button
            type="button"
            onClick={onStop}
            className="lk-btn"
            aria-label="Stop generating"
          >
            <span className="text-xs">■ Stop</span>
          </button>
        ) : (
          <button
            type="submit"
            disabled={!text.trim()}
            className="lk-btn"
            aria-label="Send message"
          >
            <SendIcon />
          </button>
        )}
      </div>
    </form>
  );
}