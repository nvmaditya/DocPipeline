"use client";

import React from "react";
import { useMemo, useState } from "react";

import { ApiClient } from "@/lib/api-client";
import { getStoredToken } from "@/lib/auth-storage";

export function AskStreamPanel() {
  const [query, setQuery] = useState("summarize study notes");
  const [status, setStatus] = useState("idle");
  const [sources, setSources] = useState<string[]>([]);
  const [tokens, setTokens] = useState<string[]>([]);
  const [answer, setAnswer] = useState("");

  const api = useMemo(() => new ApiClient(undefined, getStoredToken), []);

  async function stream() {
    setStatus("streaming...");
    setSources([]);
    setTokens([]);
    setAnswer("");

    try {
      await api.askStream(query, 5, (event) => {
        if (event.type === "meta") {
          setSources(event.sources);
          return;
        }
        if (event.type === "token") {
          setTokens((prev) => [...prev, event.content]);
          return;
        }
        setAnswer(event.answer);
      });
      setStatus("stream complete");
    } catch (error) {
      setStatus((error as Error).message);
    }
  }

  return (
    <section className="card grid">
      <h2>Ask Stream</h2>
      <label>
        Question
        <input value={query} onChange={(event) => setQuery(event.target.value)} />
      </label>
      <button onClick={stream} type="button">
        Stream Answer
      </button>
      <p className="status">{status}</p>
      <div>
        <strong>Sources</strong>
        <ul>
          {sources.map((source) => (
            <li key={source}>{source}</li>
          ))}
        </ul>
      </div>
      <div>
        <strong>Tokens</strong>
        <ul>
          {tokens.map((token, index) => (
            <li key={`${token}-${index}`}>{token}</li>
          ))}
        </ul>
      </div>
      <div>
        <strong>Final Answer</strong>
        <p>{answer}</p>
      </div>
    </section>
  );
}
