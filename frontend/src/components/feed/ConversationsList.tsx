import { ConversationListItem } from "@/types/api";
import { ConversationIcon } from "./icons";

interface ConversationsListProps {
  conversations: ConversationListItem[];
  onOpen: (id: string) => void;
}

export function ConversationsList({
  conversations,
  onOpen,
}: ConversationsListProps) {
  return (
    <section className="lk-card mb-5">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-lk-muted">
          Recent Conversations
        </h2>
        <span className="lk-badge">Coaching</span>
      </div>

      {conversations.length === 0 ? (
        <p className="text-xs text-lk-muted py-1">No active conversations yet.</p>
      ) : (
        <ul className="mt-2 space-y-1">
          {conversations.map((conv) => (
            <li key={conv.id}>
              <button
                className="w-full text-left rounded-md px-3 py-2 text-sm hover:bg-lk-user-msg transition-colors flex items-center justify-between group"
                onClick={() => onOpen(conv.id)}
              >
                <span className="flex items-center gap-2.5 truncate">
                  <ConversationIcon className="text-lk-muted group-hover:text-lk-fg transition-colors" />
                  <span className="truncate text-lk-fg font-medium">{conv.title}</span>
                </span>
                <span className="text-xs text-lk-muted shrink-0 font-mono">
                  {new Date(conv.updated_at).toLocaleDateString()}
                </span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
