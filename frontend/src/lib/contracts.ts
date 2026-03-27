export type RegisterRequest = {
  email: string;
  password: string;
};

export type RegisterResponse = {
  user_id: string;
  email: string;
};

export type LoginRequest = {
  email: string;
  password: string;
};

export type LoginResponse = {
  access_token: string;
  token_type: "bearer";
};

export type MeResponse = {
  user_id: string;
  email: string;
};

export type DocumentRecord = {
  doc_id: string;
  user_id: string;
  file_name: string;
  file_size_bytes: number;
  ingested_at: string;
  file_type: string;
  file_path: string;
};

export type DocumentListResponse = {
  documents: DocumentRecord[];
};

export type SemanticSearchRequest = {
  query: string;
  top_k?: number;
};

export type SemanticSearchResult = {
  score: number;
  file_name: string;
  [key: string]: unknown;
};

export type SemanticSearchResponse = {
  query: string;
  results: SemanticSearchResult[];
};

export type AskStreamMetaEvent = {
  type: "meta";
  query: string;
  sources: string[];
};

export type AskStreamTokenEvent = {
  type: "token";
  content: string;
};

export type AskStreamDoneEvent = {
  type: "done";
  answer: string;
};

export type AskStreamEvent = AskStreamMetaEvent | AskStreamTokenEvent | AskStreamDoneEvent;
