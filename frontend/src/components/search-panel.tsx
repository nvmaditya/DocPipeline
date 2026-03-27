"use client";

import React from "react";
import { useMemo, useState } from "react";

import { ApiClient } from "@/lib/api-client";
import { getStoredToken } from "@/lib/auth-storage";
import { SemanticSearchResult } from "@/lib/contracts";

export function SearchPanel() {
  const [query, setQuery] = useState("semantic retrieval");
  const [status, setStatus] = useState("idle");
  const [results, setResults] = useState<SemanticSearchResult[]>([]);

  const api = useMemo(() => new ApiClient(undefined, getStoredToken), []);

  async function search() {
    setStatus("searching...");
    try {
      const response = await api.semanticSearch({ query, top_k: 5 });
      setResults(response.results);
      setStatus("search complete");
    } catch (error) {
      setStatus((error as Error).message);
    }
  }

  return (
    <section className="card grid">
      <h2>Semantic Search</h2>
      <label>
        Query
        <input value={query} onChange={(event) => setQuery(event.target.value)} />
      </label>
      <button onClick={search} type="button">
        Run Search
      </button>
      <p className="status">{status}</p>
      <ul>
        {results.map((row, index) => (
          <li key={`${row.file_name}-${index}`}>
            {row.file_name} ({Number(row.score).toFixed(3)})
          </li>
        ))}
      </ul>
    </section>
  );
}
