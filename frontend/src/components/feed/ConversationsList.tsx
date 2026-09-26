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
    <section className="lk-card mb-5 mx-6">
      <h2 className="text-xs font-medium text-lk-muted mb-3">
        Conversations
      </h2>

      {conversations.length === 0 ? (
        <p className="text-xs text-lk-muted">No conversations yet.</p>
      ) : (
        <ul className="mt-2 space-y-1">
          {conversations.map((conv) => (
            <li key={conv.id}>
              <button
                className="w-full text-left rounded-sm px-2 py-1.5 text-sm hover:bg-lk-muted/5 transition-colors"
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