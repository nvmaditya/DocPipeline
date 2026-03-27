import { DocumentsPanel } from "@/components/documents-panel";

export default function DocumentsPage() {
    return (
        <main className="grid pageLayout">
            <section className="card pageIntro">
                <h1>Documents</h1>
                <p>
                    Upload files, refresh indexed records, and verify document
                    metadata before running search or ask-stream flows.
                </p>
            </section>
            <DocumentsPanel />
        </main>
    );
}
