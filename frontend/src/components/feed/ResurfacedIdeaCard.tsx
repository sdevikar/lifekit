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
    <section className="lk-card mb-5">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-lk-muted">
          Idea to Remember
        </h2>
        <span className="lk-badge">Resurfaced</span>
      </div>
      <blockquote className="text-sm italic font-serif text-lk-fg leading-relaxed">
        &ldquo;{idea.text}&rdquo;
      </blockquote>

      <p className="mt-3 text-xs text-lk-subtle bg-lk-bg p-2.5 rounded-sm border border-lk-border">
        <span className="font-semibold text-lk-fg">Why it resurfaced:</span> {idea.why}
      </p>

      <div className="mt-5 flex items-center gap-3">
        <button
          className="lk-btn lk-btn-sm"
          onClick={() => onStillWithMe(true)}
          disabled={signaling}
        >
          Still with me
        </button>
        <button
          className="lk-btn lk-btn-ghost lk-btn-sm"
          onClick={onTalkAbout}
        >
          Talk about this
        </button>
      </div>
    </section>
  );
}
