import type { Metadata } from "next";
import "./globals.css";

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
      <body className="min-h-full flex flex-col bg-lk-bg text-lk-fg antialiased">
        {children}
      </body>
    </html>
  );
}