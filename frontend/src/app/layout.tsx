import type { Metadata } from "next";
import { Newsreader, Space_Grotesk } from "next/font/google";

import { TopNav } from "@/components/top-nav";
import "./globals.css";

const displayFont = Space_Grotesk({
    variable: "--font-display",
    subsets: ["latin"],
    weight: ["400", "500", "700"],
});

const serifFont = Newsreader({
    variable: "--font-serif",
    subsets: ["latin"],
    weight: ["400", "600"],
});

export const metadata: Metadata = {
    title: "Doc Pipeline Control Room",
    description:
        "Professional workspace for authentication, document ingestion, semantic retrieval, and ask-stream workflows",
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="en">
            <body className={`${displayFont.variable} ${serifFont.variable}`}>
                <div className="shell grid shellStack">
                    <header className="card appHeader">
                        <div className="brandBlock">
                            <p className="eyebrow">Knowledge Workspace</p>
                            <strong>Doc Pipeline Control Room</strong>
                            <p>
                                Unified frontend for auth, ingestion, semantic
                                search, and streamed answers.
                            </p>
                        </div>
                        <TopNav />
                    </header>
                    {children}
                </div>
            </body>
        </html>
    );
}
