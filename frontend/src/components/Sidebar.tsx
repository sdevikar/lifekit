"use client";

import { useState, ReactNode } from "react";
import { useTab } from "./TabContext";

const COLLAPSE_KEY = "lifekit-sidebar-collapsed";

export function Sidebar() {
  const { activeTab, setActiveTab } = useTab();
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
    <aside className="flex flex-row shrink-0 sticky top-0 h-screen" suppressHydrationWarning>
      {/* Icon strip */}
      <div className="flex flex-col items-center w-14 border-r border-lk-border bg-lk-card py-3 gap-1">
        {collapsed && <div className="flex justify-end w-full px-1">{toggle}</div>}
        <IconTab
          label="Feed"
          active={activeTab === "feed"}
          onClick={() => setActiveTab("feed")}
        >
          <FeedIcon />
        </IconTab>
        <IconTab
          label="Journal"
          active={activeTab === "journal"}
          onClick={() => setActiveTab("journal")}
        >
          <JournalIcon />
        </IconTab>
        <IconTab
          label="Chat"
          active={activeTab === "chat"}
          onClick={() => setActiveTab("chat")}
        >
          <ChatIcon />
        </IconTab>
        <div className="flex-1" />
        <IconTab
          label="Settings"
          active={activeTab === "settings"}
          onClick={() => setActiveTab("settings")}
        >
          <SettingsIcon />
        </IconTab>
      </div>
      {/* Panel */}
      {!collapsed && (
        <div className="w-70 border-r border-lk-border bg-lk-card p-4 overflow-y-auto">
          <div className="flex items-start justify-between gap-2">
            {activeTab === "feed" && (
              <div>
                <h2 className="text-sm font-semibold text-lk-fg">LifeKit</h2>
                <p className="text-xs text-lk-muted mt-1">Today</p>
              </div>
            )}
            {activeTab === "journal" && (
              <p className="text-sm text-lk-muted">Coming soon.</p>
            )}
            {activeTab === "chat" && (
              <p className="text-sm text-lk-muted">Coming soon.</p>
            )}
            {activeTab === "settings" && (
              <p className="text-sm text-lk-muted">Coming soon.</p>
            )}
            <div className="shrink-0 -mt-1 -mr-1">{toggle}</div>
          </div>
        </div>
      )}
    </aside>
  );
}

function IconTab({
  label,
  active,
  onClick,
  children,
}: {
  label: string;
  active: boolean;
  onClick: () => void;
  children: ReactNode;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`flex flex-col items-center gap-1 w-12 py-2 rounded-md text-xs ${
        active
          ? "bg-lk-user-msg text-lk-fg"
          : "text-lk-muted hover:text-lk-fg hover:bg-lk-user-msg"
      }`}
      aria-label={label}
      title={label}
    >
      {children}
      <span className="text-[10px]">{label}</span>
    </button>
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
