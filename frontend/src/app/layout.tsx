import type { Metadata } from "next";
import Link from "next/link";

import "./globals.css";

export const metadata: Metadata = {
  title: "Doc Pipeline Frontend",
  description: "Phase 6 scaffold for auth, docs, search, and ask stream",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="shell grid" style={{ gap: "20px" }}>
          <header className="card" style={{ display: "flex", justifyContent: "space-between", gap: "12px", flexWrap: "wrap" }}>
            <strong>Doc Pipeline Frontend Scaffold</strong>
            <nav style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
              <Link href="/">Home</Link>
              <Link href="/login">Login</Link>
              <Link href="/documents">Documents</Link>
              <Link href="/search">Search</Link>
              <Link href="/ask">Ask Stream</Link>
            </nav>
          </header>
          {children}
        </div>
      </body>
    </html>
  );
}
