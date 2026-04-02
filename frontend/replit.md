# Workspace

## Overview

pnpm workspace monorepo using TypeScript. Each package manages its own dependencies.

## Stack

- **Monorepo tool**: pnpm workspaces
- **Node.js version**: 24
- **Package manager**: pnpm
- **TypeScript version**: 5.9
- **API framework**: Express 5
- **Database**: PostgreSQL + Drizzle ORM
- **Validation**: Zod (`zod/v4`), `drizzle-zod`
- **API codegen**: Orval (from OpenAPI spec)
- **Build**: esbuild (CJS bundle)
- **AI**: OpenAI via Replit AI Integrations (gpt-5.2 for Q&A)

## Application

DocMind - Personal Document Intelligence Workspace

A "chat + search over your own documents" platform. Users upload files (PDF, DOCX, TXT, CSV, etc.), the system chunks and indexes them, then users can do semantic search and ask grounded Q&A questions powered by AI.

### Features
- Document upload (drag-and-drop, multipart/form-data)
- Text extraction and chunking (BM25 keyword scoring for retrieval)
- Semantic search over document chunks
- Grounded Q&A using OpenAI gpt-5.2 with source citations
- Dashboard with stats
- Dark mode professional UI with sidebar navigation

## Structure

```text
artifacts-monorepo/
├── artifacts/              # Deployable applications
│   ├── api-server/         # Express API server
│   └── doc-workspace/      # React + Vite frontend (DocMind UI)
├── lib/                    # Shared libraries
│   ├── api-spec/           # OpenAPI spec + Orval codegen config
│   ├── api-client-react/   # Generated React Query hooks
│   ├── api-zod/            # Generated Zod schemas from OpenAPI
│   ├── db/                 # Drizzle ORM schema + DB connection
│   └── integrations-openai-ai-server/  # OpenAI client via Replit AI
├── scripts/                # Utility scripts
├── pnpm-workspace.yaml
├── tsconfig.base.json
├── tsconfig.json
└── package.json
```

## Database Schema

- `documents` table: id (uuid), name, fileType, fileSize, status (pending/processing/ready/error), chunkCount, createdAt, updatedAt
- `chunks` table: id (uuid), documentId (fk), content, chunkIndex, embeddingJson, createdAt

## API Routes

- `GET /api/healthz` — health check
- `GET /api/documents` — list all documents
- `GET /api/documents/:id` — get document
- `DELETE /api/documents/:id` — delete document + chunks
- `POST /api/documents/upload` — upload file (multipart), async chunk processing
- `POST /api/search` — BM25 semantic search over chunks
- `POST /api/ask` — Q&A with gpt-5.2, returns answer + sources

## TypeScript & Composite Projects

Every package extends `tsconfig.base.json` which sets `composite: true`. The root `tsconfig.json` lists all packages as project references.

- **Always typecheck from the root** — run `pnpm run typecheck`
- **`emitDeclarationOnly`** — only emit `.d.ts` files during typecheck

## Root Scripts

- `pnpm run build` — runs `typecheck` first, then recursively runs `build`
- `pnpm run typecheck` — runs `tsc --build --emitDeclarationOnly`

## Key Commands

- `pnpm --filter @workspace/api-server run dev` — run the dev server
- `pnpm --filter @workspace/api-spec run codegen` — regenerate API client
- `pnpm --filter @workspace/db run push` — push schema migrations
- `pnpm --filter @workspace/doc-workspace run dev` — run frontend dev server

## Environment Variables

- `DATABASE_URL`, `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`, `PGDATABASE` — auto-provided by Replit
- `AI_INTEGRATIONS_OPENAI_BASE_URL`, `AI_INTEGRATIONS_OPENAI_API_KEY` — auto-provided by Replit AI Integrations
- `PORT` — assigned per-artifact by Replit
