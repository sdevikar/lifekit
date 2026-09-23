import { Message } from "@/types/api";

interface MessageListProps {
  messages: Message[];
}

export function MessageList({ messages }: MessageListProps) {
  if (messages.length === 0) {
    return (
      <div className="p-4 text-center text-lk-muted">
        <p>Send a message to start the conversation.</p>
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
              ? "bg-lk-accent/5"
              : "bg-transparent")
          }
        >
          <div className="max-w-[85%] mx-auto px-3">
            <span
              className={
                "text-xs font-semibold " +
                (msg.role === "coach"
                  ? "text-lk-accent"
                  : "text-lk-muted")
              }
            >
              {msg.role === "coach" ? "Coach" : "You"}
            </span>
            <p className="mt-1 whitespace-pre-wrap">{msg.text}</p>
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