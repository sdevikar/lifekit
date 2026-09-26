import { FadingIdea } from "@/types/api";

interface FadingIdeasCardProps {
  ideas: FadingIdea[];
  onTalkAbout: (id: number) => void;
}

export function FadingIdeasCard({ ideas, onTalkAbout }: FadingIdeasCardProps) {
  if (!ideas.length) return null;

  return (
    <section className="lk-card mb-5 mx-6">
      <h2 className="text-xs font-medium text-lk-muted mb-3">
        Fading ideas
      </h2>
      <p className="text-xs text-lk-muted mb-3">
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