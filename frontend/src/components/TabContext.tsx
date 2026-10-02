"use client";

import { createContext, useContext, useState, ReactNode } from "react";

type Tab = "feed" | "journal" | "chat" | "settings";

interface TabContextValue {
  activeTab: Tab;
  setActiveTab: (tab: Tab) => void;
}

const TabContext = createContext<TabContextValue | null>(null);

export function TabProvider({ children }: { children: ReactNode }) {
  const [activeTab, setActiveTab] = useState<Tab>("feed");
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
