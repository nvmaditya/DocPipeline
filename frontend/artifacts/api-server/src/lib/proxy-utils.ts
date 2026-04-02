/**
 * Shared utilities for proxying requests to the FastAPI backend.
 */

import type { Request } from "express";

/** Base URL for the FastAPI backend. */
export const FASTAPI_URL =
  (process.env["FASTAPI_URL"] || "http://localhost:8000").trim();

/**
 * Build full URL for a FastAPI endpoint.
 * @param path - Path relative to the FastAPI root, e.g. "/api/v1/auth/login"
 */
export function fastapiUrl(path: string): string {
  return `${FASTAPI_URL}${path}`;
}

/**
 * Forward the Authorization header from the incoming Express request.
 * Returns a plain object suitable for spreading into fetch headers.
 */
export function forwardAuth(req: Request): Record<string, string> {
  const auth = req.headers["authorization"];
  return auth ? { Authorization: auth } : {};
}

/**
 * Map a FastAPI document record to the frontend Document schema.
 */
export function mapDocument(raw: Record<string, unknown>): Record<string, unknown> {
  return {
    id: raw["doc_id"] ?? raw["id"],
    name: raw["file_name"] ?? raw["name"],
    fileType: raw["file_type"] ?? raw["fileType"] ?? "unknown",
    fileSize: raw["file_size_bytes"] ?? raw["fileSize"] ?? 0,
    status: "ready",
    chunkCount: 0,
    createdAt: raw["ingested_at"] ?? new Date().toISOString(),
    updatedAt: raw["ingested_at"] ?? new Date().toISOString(),
  };
}

/**
 * Map a FastAPI search result to the frontend SearchResult schema.
 */
export function mapSearchResult(raw: Record<string, unknown>): Record<string, unknown> {
  return {
    documentId: raw["doc_id"] ?? raw["documentId"] ?? "",
    documentName: raw["file_name"] ?? raw["documentName"] ?? "Unknown",
    content: raw["chunk_text"] ?? raw["content"] ?? "",
    score: raw["score"] ?? 0,
    chunkIndex: raw["chunk_index"] ?? raw["chunkIndex"] ?? 0,
  };
}
