import { FadingIdea } from "@/types/api";

interface FadingIdeasCardProps {
  ideas: FadingIdea[];
  onTalkAbout: (id: number) => void;
}

export function FadingIdeasCard({ ideas, onTalkAbout }: FadingIdeasCardProps) {
  if (!ideas.length) return null;

  return (
    <section className="lk-card mb-5">
      <div className="flex items-center justify-between mb-2">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-lk-muted">
          Fading Ideas
        </h2>
        <span className="lk-badge">Retention</span>
      </div>
      <p className="text-xs text-lk-subtle mb-3">
        These ideas are slipping — practice or talk through them to retain them.
      </p>

      <ul className="mt-3 space-y-2 divide-y divide-lk-border">
        {ideas.map((idea) => (
          <li
            key={idea.id}
            className="pt-2 flex items-center justify-between gap-3"
          >
            <span className="text-sm text-lk-fg">{idea.text}</span>
            <button
              className="lk-btn lk-btn-sm lk-btn-ghost shrink-0"
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
