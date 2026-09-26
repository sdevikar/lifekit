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
    <section className="lk-card mb-4">
      <h2 className="text-sm font-semibold text-lk-muted uppercase tracking-wider">
        Idea to Remember
      </h2>
      <blockquote className="mt-2 text-lg italic">"{idea.text}"</blockquote>

      <p className="mt-2 text-sm text-lk-muted">
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