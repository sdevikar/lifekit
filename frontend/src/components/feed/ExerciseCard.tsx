import { ExerciseCard as ExerciseCardData } from "@/types/api";

interface ExerciseCardProps {
  exercise: ExerciseCardData;
  onMarkDone: () => void;
  onTalkAbout: () => void;
  markingDone?: boolean;
}

export function ExerciseCard({
  exercise,
  onMarkDone,
  onTalkAbout,
  markingDone = false,
}: ExerciseCardProps) {
  return (
    <section className="lk-card mb-5">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-lk-muted">
          Today&apos;s Exercise
        </h2>
        <span className="lk-badge">Action</span>
      </div>
      <p className="text-sm text-lk-fg font-normal leading-relaxed">{exercise.text}</p>

      {exercise.source_quote && (
        <blockquote className="mt-3.5 border-l-2 border-lk-brand-clay pl-3.5 text-sm italic font-serif text-lk-subtle bg-lk-bg/60 py-2 rounded-r-sm">
          &ldquo;{exercise.source_quote}&rdquo;
        </blockquote>
      )}

      <div className="mt-5 flex items-center gap-3">
        <button
          className="lk-btn lk-btn-clay lk-btn-sm"
          onClick={onMarkDone}
          disabled={markingDone}
        >
          {markingDone ? "Saving…" : "Mark done"}
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
