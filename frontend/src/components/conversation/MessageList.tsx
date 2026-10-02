"use client";

import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Message } from "@/types/api";

interface MessageListProps {
  messages: Message[];
}

export function MessageList({ messages }: MessageListProps) {
  if (messages.length === 0) {
    return (
      <div className="lk-shell py-12 text-center text-lk-muted">
        <p className="text-sm">Send a message to start conversing with your coach.</p>
      </div>
    );
  }

  return (
    <div className="lk-shell py-6 space-y-4">
      {messages.map((msg, i) => {
        const isCoach = msg.role === "coach";
        return (
          <div
            key={i}
            className={`flex flex-col ${isCoach ? "items-start" : "items-end"}`}
          >
            <div className="flex items-center gap-2 mb-1 px-1">
              <span
                className={`text-xs font-medium ${
                  isCoach ? "text-lk-secondary font-semibold" : "text-lk-muted"
                }`}
              >
                {isCoach ? "Coach" : "You"}
              </span>
              <time className="text-[11px] text-lk-muted/70 font-mono">
                {new Date(msg.created_at).toLocaleTimeString([], {
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </time>
            </div>

            <div
              className={`max-w-[85%] rounded-lg p-3.5 text-sm leading-relaxed ${
                isCoach
                  ? "bg-lk-card border border-lk-border shadow-xs text-lk-fg font-serif"
                  : "bg-lk-user-msg border border-lk-border/60 text-lk-fg"
              }`}
            >
              {isCoach ? (
                // react-markdown escapes by default — no dangerouslySetInnerHTML,
                // so a reply containing `<script>` renders as visible text.
                <div className="lk-prose">
                  <Markdown remarkPlugins={[remarkGfm]}>{msg.text}</Markdown>
                </div>
              ) : (
                // User text is typed by the human and is never interpreted.
                <p className="whitespace-pre-wrap">{msg.text}</p>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
