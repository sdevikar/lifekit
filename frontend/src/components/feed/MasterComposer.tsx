import { useState } from "react";
import { SendIcon } from "./icons";

interface MasterComposerProps {
  onSubmit: (text: string) => void;
  submitting?: boolean;
}

export function MasterComposer({ onSubmit, submitting = false }: MasterComposerProps) {
  const [text, setText] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = text.trim();
    if (!trimmed || submitting) return;
    onSubmit(trimmed);
    setText("");
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="fixed bottom-0 left-0 right-0 p-4 bg-lk-bg/95 backdrop-blur-sm border-t border-lk-border shadow-panel z-10"
    >
      <div className="lk-shell">
        <div className="flex gap-2">
          <input
            type="text"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Ask about an exercise or start a coach conversation…"
            className="lk-input flex-1"
            disabled={submitting}
            maxLength={500}
          />
          <button
            type="submit"
            disabled={!text.trim() || submitting}
            className="lk-btn"
          >
            {submitting ? "Sending…" : <SendIcon />}
          </button>
        </div>
        <p className="mt-1.5 text-xs text-lk-muted">
          Opens a grounded coach conversation anchored in book knowledge.
        </p>
      </div>
    </form>
  );
}
