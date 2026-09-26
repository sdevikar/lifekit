import { ResurfacedIdea } from "@/types/api";

interface ResurfacedIdeaCardProps {
  idea: ResurfacedIdea;
  onStillWithMe: (remembered: boolean) => void;
  onTalkAbout: () => void;
  signaling?: boolean;
}

export function ResurfacedIdeaCard({
  idea,
  onStillWithMe,
  onTalkAbout,
  signaling = false,
}: ResurfacedIdeaCardProps) {
  return (
    <section className="lk-card mb-5 mx-6">
      <h2 className="text-xs font-medium text-lk-muted mb-3">
        Idea to remember
      </h2>
      <blockquote className="text-sm italic">&ldquo;{idea.text}&rdquo;</blockquote>

      <p className="mt-2 text-xs text-lk-muted">
        <span className="font-medium">Why it resurfaced:</span> {idea.why}
      </p>

      <div className="mt-4 flex gap-2">
        <button
          className="lk-btn lk-btn-sm"
          onClick={() => onStillWithMe(true)}
          disabled={signaling}
        >
          Still with me
        </button>
        <button
          className="lk-btn lk-btn-sm lk-btn-secondary"
          onClick={onTalkAbout}
        >
          Talk about this
        </button>
      </div>
    </section>
  );
}