"use client";

import { createContext, useContext, useState, ReactNode, useEffect } from "react";
import { usePathname } from "next/navigation";

export type Tab = "feed" | "journal" | "chat" | "settings";

interface TabContextValue {
  activeTab: Tab;
  setActiveTab: (tab: Tab) => void;
}

const TabContext = createContext<TabContextValue | null>(null);

function tabFromPath(pathname: string): Tab {
  if (pathname.startsWith("/chat")) return "chat";
  if (pathname.startsWith("/journal")) return "journal";
  if (pathname.startsWith("/feed")) return "feed";
  return "feed";
}

export function TabProvider({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const [activeTab, setActiveTab] = useState<Tab>(() => tabFromPath(pathname));

  useEffect(() => {
    setActiveTab(tabFromPath(pathname));
  }, [pathname]);

  return (
    <TabContext.Provider value={{ activeTab, setActiveTab }}>
      {children}
    </TabContext.Provider>
  );
}

export function useTab() {
  const ctx = useContext(TabContext);
  if (!ctx) throw new Error("useTab must be used within TabProvider");
  return ctx;
}
