import { Message } from "@/types/api";

interface MessageListProps {
  messages: Message[];
}

export function MessageList({ messages }: MessageListProps) {
  if (messages.length === 0) {
    return (
      <div className="p-6 text-center text-lk-muted">
        <p className="text-sm">Send a message to start the conversation.</p>
      </div>
    );
  }

  return (
    <ul className="divide-y divide-lk-border">
      {messages.map((msg, i) => (
        <li
          key={i}
          className={
            "py-3 " +
            (msg.role === "coach"
              ? "bg-lk-secondary/5"
              : "bg-transparent")
          }
        >
          <div className="max-w-[785px] mx-auto px-6">
            <span
              className={
                "text-xs font-medium " +
                (msg.role === "coach"
                  ? "text-lk-secondary"
                  : "text-lk-muted")
              }
            >
              {msg.role === "coach" ? "Coach" : "You"}
            </span>
            <p className="mt-1 whitespace-pre-wrap text-sm">{msg.text}</p>
            <time className="text-xs text-lk-muted opacity-60">
              {new Date(msg.created_at).toLocaleTimeString([], {
                hour: "2-digit",
                minute: "2-digit",
              })}
            </time>
          </div>
        </li>
      ))}
    </ul>
  );
}