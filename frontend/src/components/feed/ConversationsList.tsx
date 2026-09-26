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
    <section className="lk-card mb-4">
      <h2 className="text-sm font-semibold text-lk-muted uppercase tracking-wider">
        Conversations
      </h2>

      {conversations.length === 0 ? (
        <p className="mt-3 text-sm text-lk-muted">No conversations yet.</p>
      ) : (
        <ul className="mt-2 space-y-1">
          {conversations.map((conv) => (
            <li key={conv.id}>
              <button
                className="w-full text-left rounded-md px-2 py-1.5 text-sm hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                onClick={() => onOpen(conv.id)}
              >
                <span className="flex items-center gap-2">
                  <ConversationIcon />
                  <span className="truncate">{conv.title}</span>
                </span>
                <span className="block text-xs text-lk-muted">
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