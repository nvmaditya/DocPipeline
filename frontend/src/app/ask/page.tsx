import { AskStreamPanel } from "@/components/ask-stream-panel";

export default function AskPage() {
    return (
        <main className="grid pageLayout">
            <section className="card pageIntro">
                <h1>Ask Stream</h1>
                <p>
                    Stream grounded answers in real time and review source
                    traces and token output during generation.
                </p>
            </section>
            <AskStreamPanel />
        </main>
    );
}
