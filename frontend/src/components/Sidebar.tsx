"use client";

import { useState, ReactNode } from "react";
import { useRouter } from "next/navigation";
import { useTab } from "./TabContext";
import { RecentConversations } from "./sidebar/RecentConversations";

const COLLAPSE_KEY = "lifekit-sidebar-collapsed";

export function Sidebar() {
  const { activeTab, setActiveTab } = useTab();
  const router = useRouter();
  const [collapsed, setCollapsed] = useState(() => {
    if (typeof window === "undefined") return false;
    return localStorage.getItem(COLLAPSE_KEY) === "true";
  });

  const toggleCollapse = () => {
    const next = !collapsed;
    setCollapsed(next);
    localStorage.setItem(COLLAPSE_KEY, String(next));
  };

  const toggle = (
    <button
      type="button"
      onClick={toggleCollapse}
      className="lk-btn lk-btn-sm lk-btn-ghost px-2"
      aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
      title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
    >
      {collapsed ? <PanelLeftOpenIcon /> : <PanelLeftCloseIcon />}
    </button>
  );

  return (
    <aside
      className={`flex flex-col shrink-0 sticky top-0 h-screen border-r border-lk-border bg-lk-card ${
        collapsed ? "w-10" : "w-70"
      }`}
      suppressHydrationWarning
    >
      {/* Header — collapse toggle sits top-right expanded, alone when collapsed. */}
      <div className="flex items-center justify-between gap-2 px-2 py-3 shrink-0">
        {collapsed ? (
          <div className="flex justify-center w-full">{toggle}</div>
        ) : (
          toggle
        )}
      </div>

      <nav className="flex flex-col gap-0.5 px-2 shrink-0">
        <NavRow
          label="Feed"
          active={activeTab === "feed"}
          collapsed={collapsed}
          onClick={() => router.push("/feed")}
        >
          <FeedIcon />
        </NavRow>
        <NavRow
          label="Journal"
          active={activeTab === "journal"}
          collapsed={collapsed}
          onClick={() => router.push("/journal")}
        >
          <JournalIcon />
        </NavRow>
        <NavRow
          label="Chat"
          active={activeTab === "chat"}
          collapsed={collapsed}
          onClick={() => router.push("/chat")}
        >
          <ChatIcon />
        </NavRow>
      </nav>

      {/* Tab content owns the leftover height — flex-1 here, and only here, so
          Settings below it gets pinned to the bottom of the column. When two
          siblings are flex-1 they split the space and Settings floats in the
          middle. Also acts as the spacer, so it must render even collapsed. */}
      <div className="flex-1 min-h-0 overflow-y-auto px-2">
        {!collapsed && activeTab === "chat" && <RecentConversations />}
        {!collapsed && activeTab === "settings" && (
          <p className="text-sm text-lk-muted">Coming soon.</p>
        )}
      </div>

      <nav className="flex flex-col gap-0.5 px-2 py-2 shrink-0 border-t border-lk-border">
        <NavRow
          label="Settings"
          active={activeTab === "settings"}
          collapsed={collapsed}
          onClick={() => setActiveTab("settings")}
        >
          <SettingsIcon />
        </NavRow>
      </nav>
    </aside>
  );
}

function NavRow({
  label,
  active,
  collapsed,
  onClick,
  children,
}: {
  label: string;
  active: boolean;
  collapsed: boolean;
  onClick: () => void;
  children: ReactNode;
}) {
  return (
    <div className="group relative flex items-center">
      <button
        type="button"
        onClick={onClick}
        className={`flex items-center gap-2.5 w-full rounded-md text-sm transition-colors ${
          collapsed ? "justify-center px-2 py-2" : "px-3 py-2"
        } ${
          active
            ? "bg-lk-user-msg text-lk-fg"
            : "text-lk-muted hover:text-lk-fg hover:bg-lk-user-msg"
        }`}
        aria-label={label}
        title={label}
      >
        <span className="shrink-0 flex items-center">{children}</span>
        {/* Not rendered when collapsed — no shrunk or clipped labels. The
            button keeps aria-label and title, so the strip stays labelled. */}
        {!collapsed && <span className="truncate">{label}</span>}
      </button>
    </div>
  );
}

function FeedIcon() {
  return (
    <svg
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
      <polyline points="9 22 9 12 15 12 15 22" />
    </svg>
  );
}

function JournalIcon() {
  return (
    <svg
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
      <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
    </svg>
  );
}

function ChatIcon() {
  return (
    <svg
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z" />
    </svg>
  );
}

function SettingsIcon() {
  return (
    <svg
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <circle cx="12" cy="12" r="3" />
      <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" />
    </svg>
  );
}

function PanelLeftOpenIcon() {
  return (
    <svg
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <rect width="18" height="18" x="3" y="3" rx="2" />
      <path d="M9 3v18" />
      <path d="m14 9 3 3-3 3" />
    </svg>
  );
}

function PanelLeftCloseIcon() {
  return (
    <svg
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <rect width="18" height="18" x="3" y="3" rx="2" />
      <path d="M9 3v18" />
      <path d="m16 15-3-3 3-3" />
    </svg>
  );
}
