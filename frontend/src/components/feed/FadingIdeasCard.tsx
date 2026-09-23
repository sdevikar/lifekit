import { FadingIdea } from "@/types/api";

interface FadingIdeasCardProps {
  ideas: FadingIdea[];
  onTalkAbout: (id: number) => void;
}

export function FadingIdeasCard({ ideas, onTalkAbout }: FadingIdeasCardProps) {
  if (!ideas.length) return null;

  return (
    <section className="lk-card mb-4">
      <h2 className="text-sm font-semibold text-lk-muted uppercase tracking-wider">
        Fading Ideas
      </h2>
      <p className="mt-1 text-sm text-lk-muted">
        These ideas are slipping — reflect on them.
      </p>

      <ul className="mt-3 space-y-2">
        {ideas.map((idea) => (
          <li
            key={idea.id}
            className="flex items-start justify-between gap-3"
          >
            <span className="text-sm">{idea.text}</span>
            <button
              className="lk-btn lk-btn-sm lk-btn-secondary shrink-0"
              onClick={() => onTalkAbout(idea.id)}
            >
              Talk about this
            </button>
          </li>
        ))}
      </ul>
    </section>
  );
}