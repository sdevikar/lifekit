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
      className="fixed bottom-0 left-0 right-0 p-4 bg-lk-bg border-t border-lk-border"
    >
      <div className="max-w-[785px] mx-auto">
        <div className="flex gap-2">
          <input
            type="text"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Ask about an exercise or idea…"
            className="flex-1 px-3 py-2 border border-lk-border rounded-sm focus:outline-none focus:border-lk-primary"
            disabled={submitting}
            maxLength={500}
          />
          <button
            type="submit"
            disabled={!text.trim() || submitting}
            className="lk-btn lk-btn-sm"
          >
            {submitting ? "Sending…" : <SendIcon />}
          </button>
        </div>
        <p className="mt-1 text-xs text-lk-muted">
          Creates a new conversation grounded in the book.
        </p>
      </div>
    </form>
  );
}