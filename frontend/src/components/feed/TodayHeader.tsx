import { ThemeToggle } from "@/components/ThemeToggle";
import { BookInfo, StageStrip } from "@/types/api";

interface TodayHeaderProps {
  book: BookInfo;
  day: string;
  stages: StageStrip;
}

export function TodayHeader({ book, day, stages }: TodayHeaderProps) {
  return (
    <header className="mb-6 pt-6">
      <div className="flex items-baseline justify-between">
        <div>
          <span className="lk-badge mb-1.5">Daily briefing</span>
          <h1 className="text-2xl font-normal tracking-tight text-lk-fg">
            {book.title}
          </h1>
        </div>
        <div className="flex items-center gap-3">
          <time className="text-xs text-lk-muted font-mono">{day}</time>
          <ThemeToggle />
        </div>
      </div>

      {/* Stage strip — ideas seen → retained → lived */}
      <nav className="mt-5 flex items-center justify-around py-3 px-4 bg-lk-card rounded-md border border-lk-border shadow-xs">
        <StageItem label="Seen" value={stages.seen} />
        <div className="h-4 w-px bg-lk-border" />
        <StageItem label="Retained" value={stages.retained} />
        <div className="h-4 w-px bg-lk-border" />
        <StageItem label="Lived" value={stages.lived} />
      </nav>
    </header>
  );
}

function StageItem({ label, value }: { label: string; value: number }) {
  return (
    <div className="flex items-center gap-2">
      <span className="text-lg font-semibold text-lk-fg font-mono">{value}</span>
      <span className="text-xs text-lk-muted uppercase tracking-wider">{label}</span>
    </div>
  );
}
