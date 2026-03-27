import {
  AskStreamEvent,
  DocumentListResponse,
  DocumentRecord,
  LoginRequest,
  LoginResponse,
  MeResponse,
  RegisterRequest,
  RegisterResponse,
  SemanticSearchRequest,
  SemanticSearchResponse,
} from "./contracts";

const DEFAULT_API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

export function parseSsePayload(buffer: string): { events: AskStreamEvent[]; remainder: string } {
  const chunks = buffer.split("\n\n");
  const completed = chunks.slice(0, -1);
  const remainder = chunks[chunks.length - 1] ?? "";

  const events: AskStreamEvent[] = [];
  for (const chunk of completed) {
    const line = chunk
      .split("\n")
      .map((entry) => entry.trim())
      .find((entry) => entry.startsWith("data:"));
    if (!line) {
      continue;
    }
    const raw = line.slice(5).trim();
    try {
      const parsed = JSON.parse(raw) as AskStreamEvent;
      events.push(parsed);
    } catch {
      // Ignore malformed SSE payload fragments.
    }
  }

  return { events, remainder };
}

export class ApiClient {
  constructor(
    private readonly baseUrl: string = DEFAULT_API_BASE,
    private readonly getToken?: () => string | null,
  ) {}

  private async request<T>(path: string, init: RequestInit = {}): Promise<T> {
    const headers = new Headers(init.headers ?? {});
    if (!headers.has("Content-Type") && !(init.body instanceof FormData)) {
      headers.set("Content-Type", "application/json");
    }

    const token = this.getToken?.();
    if (token) {
      headers.set("Authorization", `Bearer ${token}`);
    }

    const response = await fetch(`${this.baseUrl}${path}`, {
      ...init,
      headers,
    });

    if (!response.ok) {
      const detail = await response.text();
      throw new Error(`HTTP ${response.status}: ${detail || response.statusText}`);
    }

    if (response.status === 204) {
      return undefined as T;
    }

    return (await response.json()) as T;
  }

  register(payload: RegisterRequest): Promise<RegisterResponse> {
    return this.request<RegisterResponse>("/api/v1/auth/register", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  login(payload: LoginRequest): Promise<LoginResponse> {
    return this.request<LoginResponse>("/api/v1/auth/login", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  me(): Promise<MeResponse> {
    return this.request<MeResponse>("/api/v1/auth/me", {
      method: "GET",
    });
  }

  async uploadDocument(file: File): Promise<Pick<DocumentRecord, "doc_id" | "file_name" | "file_size_bytes" | "ingested_at">> {
    const form = new FormData();
    form.append("file", file);
    return this.request("/api/v1/docs/upload", {
      method: "POST",
      body: form,
    });
  }

  listDocuments(): Promise<DocumentListResponse> {
    return this.request<DocumentListResponse>("/api/v1/docs/list", {
      method: "GET",
    });
  }

  semanticSearch(payload: SemanticSearchRequest): Promise<SemanticSearchResponse> {
    return this.request<SemanticSearchResponse>("/api/v1/search/semantic", {
      method: "POST",
      body: JSON.stringify({ query: payload.query, top_k: payload.top_k ?? 5 }),
    });
  }

  async askStream(
    query: string,
    topK: number,
    onEvent: (event: AskStreamEvent) => void,
  ): Promise<void> {
    const token = this.getToken?.();
    const headers = new Headers();
    if (token) {
      headers.set("Authorization", `Bearer ${token}`);
    }

    const response = await fetch(
      `${this.baseUrl}/api/v1/search/ask/stream?query=${encodeURIComponent(query)}&top_k=${topK}`,
      { method: "GET", headers },
    );

    if (!response.ok || !response.body) {
      const detail = await response.text();
      throw new Error(`HTTP ${response.status}: ${detail || response.statusText}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let remainder = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) {
        break;
      }
      remainder += decoder.decode(value, { stream: true });
      const parsed = parseSsePayload(remainder);
      remainder = parsed.remainder;
      for (const event of parsed.events) {
        onEvent(event);
      }
    }

    if (remainder.trim()) {
      const parsed = parseSsePayload(`${remainder}\n\n`);
      for (const event of parsed.events) {
        onEvent(event);
      }
    }
  }
}
