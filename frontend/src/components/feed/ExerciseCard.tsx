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
    <section className="lk-card mb-5 mx-6">
      <h2 className="text-xs font-medium text-lk-muted mb-3">
        Today&apos;s exercise
      </h2>
      <p className="text-sm">{exercise.text}</p>

      {exercise.source_quote && (
        <blockquote className="mt-3 border-l-2 border-lk-primary pl-3 text-sm italic text-lk-muted">
          {exercise.source_quote}
        </blockquote>
      )}

      <div className="mt-4 flex gap-2">
        <button
          className="lk-btn lk-btn-sm"
          onClick={onMarkDone}
          disabled={markingDone}
        >
          {markingDone ? "Saving…" : "Mark done"}
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