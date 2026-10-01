import type { Metadata } from "next";
import "./globals.css";
import { TabProvider } from "@/components/TabContext";
import { Sidebar } from "@/components/Sidebar";
import { TabContent } from "@/components/TabContent";

export const metadata: Metadata = {
  title: "LifeKit",
  description: "Daily coaching: one exercise, one idea.",
};

// Applies the stored theme before first paint. Without this, a user whose OS
// prefers dark (or who chose dark in-app) gets a flash of the light theme on
// every load. Must stay in sync with ThemeToggle's STORAGE_KEY.
const themeScript = `try{var t=localStorage.getItem("lifekit-theme");if(t==="dark"||t==="light"){document.documentElement.dataset.theme=t}}catch(e){}`;

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeScript }} />
      </head>
      <body className="min-h-full bg-lk-bg text-lk-fg antialiased">
        <TabProvider>
          <div className="flex flex-row min-h-full">
            <Sidebar />
            <main className="flex-1 min-w-0">
              <TabContent>{children}</TabContent>
            </main>
          </div>
        </TabProvider>
      </body>
    </html>
  );
}