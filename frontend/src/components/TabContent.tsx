"use client";

import { useTab } from "./TabContext";

export function TabContent({ children }: { children: React.ReactNode }) {
  const { activeTab } = useTab();

  if (activeTab === "feed") {
    return <>{children}</>;
  }

  return (
    <div className="lk-shell py-12">
      <p className="text-sm text-lk-muted">Coming soon.</p>
    </div>
  );
}
