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
    <section className="lk-card mb-4">
      <h2 className="text-sm font-semibold text-lk-muted uppercase tracking-wider">
        Today's Exercise
      </h2>
      <p className="mt-2 text-lg">{exercise.text}</p>

      {exercise.source_quote && (
        <blockquote className="mt-3 border-l-2 border-lk-accent pl-3 text-sm italic text-lk-muted">
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