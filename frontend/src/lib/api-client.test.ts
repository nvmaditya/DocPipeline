import { beforeEach, describe, expect, it, vi } from "vitest";

import { ApiClient, parseSsePayload } from "./api-client";

describe("parseSsePayload", () => {
  it("parses completed events and keeps remainder", () => {
    const input =
      'data: {"type":"meta","query":"q","sources":["a.txt"]}\n\n' +
      'data: {"type":"token","content":"chunk"}\n\n' +
      'data: {"type":"done"';

    const parsed = parseSsePayload(input);

    expect(parsed.events).toHaveLength(2);
    expect(parsed.events[0]).toMatchObject({ type: "meta" });
    expect(parsed.events[1]).toMatchObject({ type: "token" });
    expect(parsed.remainder).toContain('data: {"type":"done"');
  });
});

describe("ApiClient", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("attaches bearer token for protected request", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ user_id: "u1", email: "student@example.com" }),
    });
    vi.stubGlobal("fetch", fetchMock);

    const api = new ApiClient("http://127.0.0.1:8000", () => "dev-token-abc");
    const me = await api.me();

    expect(me.user_id).toBe("u1");
    const init = fetchMock.mock.calls[0][1] as RequestInit;
    const headers = init.headers as Headers;
    expect(headers.get("Authorization")).toBe("Bearer dev-token-abc");
  });

  it("executes login-upload-search workflow", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ access_token: "dev-token-u1", token_type: "bearer" }),
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({
          doc_id: "d1",
          file_name: "notes.txt",
          file_size_bytes: 10,
          ingested_at: "2026-01-01T00:00:00Z",
        }),
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ query: "notes", results: [{ score: 0.91, file_name: "notes.txt" }] }),
      });

    vi.stubGlobal("fetch", fetchMock);

    let token: string | null = null;
    const api = new ApiClient("http://127.0.0.1:8000", () => token);

    const login = await api.login({ email: "student@example.com", password: "password123" });
    token = login.access_token;

    const file = new File(["hello notes"], "notes.txt", { type: "text/plain" });
    const upload = await api.uploadDocument(file);
    const search = await api.semanticSearch({ query: "notes", top_k: 5 });

    expect(upload.doc_id).toBe("d1");
    expect(search.results[0].file_name).toBe("notes.txt");
    expect(fetchMock).toHaveBeenCalledTimes(3);
  });

  it("streams ask events in order", async () => {
    const payload =
      'data: {"type":"meta","query":"q","sources":["a.txt"]}\n\n' +
      'data: {"type":"token","content":"hello"}\n\n' +
      'data: {"type":"done","answer":"hello"}\n\n';

    const stream = new ReadableStream<Uint8Array>({
      start(controller) {
        controller.enqueue(new TextEncoder().encode(payload));
        controller.close();
      },
    });

    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        body: stream,
      }),
    );

    const events: string[] = [];
    const api = new ApiClient("http://127.0.0.1:8000", () => "dev-token-u1");

    await api.askStream("question", 5, (event) => events.push(event.type));

    expect(events).toEqual(["meta", "token", "done"]);
  });

  it("throws for non-ok response", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 401,
        statusText: "Unauthorized",
        text: async () => "invalid token",
      }),
    );

    const api = new ApiClient("http://127.0.0.1:8000", () => "bad");

    await expect(api.me()).rejects.toThrow("HTTP 401");
  });
});
