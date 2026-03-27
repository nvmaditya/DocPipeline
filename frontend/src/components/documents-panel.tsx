"use client";

import React from "react";
import { useMemo, useState } from "react";

import { ApiClient } from "@/lib/api-client";
import { getStoredToken } from "@/lib/auth-storage";
import { DocumentRecord } from "@/lib/contracts";

export function DocumentsPanel() {
  const [status, setStatus] = useState("idle");
  const [selected, setSelected] = useState<File | null>(null);
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);

  const api = useMemo(() => new ApiClient(undefined, getStoredToken), []);

  async function upload() {
    if (!selected) {
      setStatus("select a file first");
      return;
    }

    setStatus("uploading...");
    try {
      await api.uploadDocument(selected);
      const rows = await api.listDocuments();
      setDocuments(rows.documents);
      setStatus("upload complete");
    } catch (error) {
      setStatus((error as Error).message);
    }
  }

  async function refresh() {
    setStatus("loading...");
    try {
      const rows = await api.listDocuments();
      setDocuments(rows.documents);
      setStatus("list refreshed");
    } catch (error) {
      setStatus((error as Error).message);
    }
  }

  return (
    <section className="card grid">
      <h2>Documents</h2>
      <label>
        Upload file
        <input
          aria-label="file"
          type="file"
          onChange={(event) => setSelected(event.target.files?.[0] ?? null)}
        />
      </label>
      <div style={{ display: "flex", gap: "8px" }}>
        <button onClick={upload} type="button">
          Upload
        </button>
        <button className="ghost" onClick={refresh} type="button">
          Refresh List
        </button>
      </div>
      <p className="status">{status}</p>
      <ul>
        {documents.map((doc) => (
          <li key={doc.doc_id}>
            {doc.file_name} <span className="badge">{doc.file_type}</span>
          </li>
        ))}
      </ul>
    </section>
  );
}
