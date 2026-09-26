import { BookInfo, StageStrip } from "@/types/api";

interface TodayHeaderProps {
  book: BookInfo;
  day: string;
  stages: StageStrip;
}

export function TodayHeader({ book, day, stages }: TodayHeaderProps) {
  return (
    <header className="mb-6">
      <div className="flex items-baseline justify-between">
        <h1 className="text-2xl font-bold">{book.title}</h1>
        <time className="text-sm text-lk-muted">{day}</time>
      </div>

      {/* Stage strip — ideas seen → retained → lived */}
      <nav className="mt-4 flex items-center gap-6">
        <StageItem label="Seen" value={stages.seen} />
        <StageItem label="Retained" value={stages.retained} />
        <StageItem label="Lived" value={stages.lived} />
      </nav>
    </header>
  );
}

function StageItem({ label, value }: { label: string; value: number }) {
  return (
    <div className="flex items-center gap-2">
      <span className="text-2xl font-semibold">{value}</span>
      <span className="text-sm text-lk-muted">{label}</span>
    </div>
  );
}