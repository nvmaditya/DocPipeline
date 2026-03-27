export default function HomePage() {
    return (
        <main className="grid">
            <section className="card pageIntro">
                <h1>Operational Workspace for Your Document Pipeline</h1>
                <p className="lead">
                    This interface is tuned for daily usage instead of a demo
                    scaffold. Navigate through auth, ingestion, retrieval, and
                    ask-stream workflows with stable backend contracts.
                </p>
            </section>
            <div className="grid two">
                <section className="card pageIntro">
                    <h2>Feature Coverage</h2>
                    <p>
                        Includes tested flows for identity, document upload,
                        semantic retrieval, and streamed Q&A responses.
                    </p>
                </section>
                <section className="card pageIntro">
                    <h2>Contract Coverage</h2>
                    <ul className="resultList">
                        <li>/api/v1/auth/register, /login, /me</li>
                        <li>/api/v1/docs/upload, /list, /{"{"}doc_id{"}"}</li>
                        <li>/api/v1/search/semantic, /ask/stream</li>
                    </ul>
                </section>
            </div>
        </main>
    );
}
