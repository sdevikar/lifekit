import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "LifeKit",
  description: "Daily coaching: one exercise, one idea.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full">
      <body className="min-h-full flex flex-col bg-lk-bg text-lk-fg antialiased">
        {children}
      </body>
    </html>
  );
}