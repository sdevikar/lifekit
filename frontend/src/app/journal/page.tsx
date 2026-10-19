"use client";

export default function JournalPage() {
  return (
    <div className="flex flex-col min-h-screen bg-lk-bg">
      <header className="border-b border-lk-border py-3.5 bg-lk-card sticky top-0 z-20 shadow-xs">
        <div className="lk-shell flex items-center justify-between gap-4">
          <h1 className="text-sm font-semibold text-lk-fg">Journal</h1>
        </div>
      </header>

      <main className="flex-1 flex items-center justify-center p-8">
        <p className="text-sm text-lk-muted">Coming soon.</p>
      </main>
    </div>
  );
}
