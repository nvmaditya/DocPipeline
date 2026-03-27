export default function HomePage() {
  return (
    <main className="grid two">
      <section className="card">
        <h1>Phase 6 Started</h1>
        <p>
          This scaffold targets current live backend contracts for auth, documents, semantic search, and ask-stream SSE.
        </p>
      </section>
      <section className="card">
        <h2>Contract Coverage</h2>
        <ul>
          <li>/api/v1/auth/register, /login, /me</li>
          <li>/api/v1/docs/upload, /list, /{`{doc_id}`}</li>
          <li>/api/v1/search/semantic, /ask/stream</li>
        </ul>
      </section>
    </main>
  );
}
