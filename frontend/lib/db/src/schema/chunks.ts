import { pgTable, text, integer, real, timestamp, uuid } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod/v4";

export const chunksTable = pgTable("chunks", {
  id: uuid("id").primaryKey().defaultRandom(),
  documentId: uuid("document_id").notNull(),
  content: text("content").notNull(),
  chunkIndex: integer("chunk_index").notNull(),
  embeddingJson: text("embedding_json"),
  createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
});

export const insertChunkSchema = createInsertSchema(chunksTable).omit({
  id: true,
  createdAt: true,
});

export type InsertChunk = z.infer<typeof insertChunkSchema>;
export type Chunk = typeof chunksTable.$inferSelect;
