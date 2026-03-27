import { SearchPanel } from "@/components/search-panel";

export default function SearchPage() {
    return (
        <main className="grid pageLayout">
            <section className="card pageIntro">
                <h1>Semantic Search</h1>
                <p>
                    Query indexed content and inspect ranked matches to validate
                    retrieval quality.
                </p>
            </section>
            <SearchPanel />
        </main>
    );
}
