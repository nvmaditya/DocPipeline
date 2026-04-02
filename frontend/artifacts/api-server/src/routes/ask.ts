import { Router, type IRouter } from "express";
import { fastapiUrl, forwardAuth, mapSearchResult } from "../lib/proxy-utils";

const router: IRouter = Router();

router.post("/ask", async (req, res): Promise<void> => {
  try {
    const { question, documentIds, databaseId } = req.body;

    // Build query params for FastAPI — include database_id if provided (community scoping)
    const searchParams: Record<string, string> = {};
    if (databaseId) searchParams["database_id"] = databaseId;
    const searchQs = new URLSearchParams(searchParams).toString();
    const searchSuffix = searchQs ? `?${searchQs}` : "";

    // Step 1: Get search results for context via semantic search
    const searchUpstream = await fetch(fastapiUrl(`/api/v1/search/semantic${searchSuffix}`), {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...forwardAuth(req),
      },
      body: JSON.stringify({ query: question, top_k: 5 }),
    });

    if (!searchUpstream.ok) {
      const err = await searchUpstream.json().catch(() => ({}));
      res.status(searchUpstream.status).json(err);
      return;
    }

    const searchData = (await searchUpstream.json()) as { results: Record<string, unknown>[] };
    const searchResults = searchData.results || [];

    if (searchResults.length === 0) {
      res.json({
        answer:
          "I couldn't find relevant information in the documents to answer this question. Please make sure the knowledge base contains information about this topic.",
        sources: [],
        question,
      });
      return;
    }

    // Step 2: Call the ask-stream endpoint to get a grounded answer
    const askParams = new URLSearchParams({ query: question, top_k: "5" });
    if (databaseId) askParams.set("database_id", databaseId);
    const askUpstream = await fetch(fastapiUrl(`/api/v1/search/ask/stream?${askParams}`), {
      headers: { ...forwardAuth(req) },
    });

    if (!askUpstream.ok) {
      const err = await askUpstream.text().catch(() => "");
      res.status(askUpstream.status).json({ error: "ask_failed", message: err || "Ask stream failed" });
      return;
    }

    // Step 3: Parse SSE response to extract the answer
    const sseText = await askUpstream.text();
    let answer = "";

    for (const line of sseText.split("\n")) {
      if (line.startsWith("data:")) {
        try {
          const payload = JSON.parse(line.slice(5).trim());
          if (payload.type === "chunk" && payload.text) {
            answer += payload.text;
          } else if (payload.type === "answer" && payload.text) {
            answer = payload.text;
          }
        } catch {
          // Not JSON, treat as plain text chunk
          const text = line.slice(5).trim();
          if (text) answer += text;
        }
      }
    }

    if (!answer) {
      answer = "I was unable to generate an answer from the retrieved documents. Please try rephrasing your question.";
    }

    // Step 4: Build sources from search results
    const sources = searchResults.slice(0, 5).map((r) => {
      const mapped = mapSearchResult(r);
      return {
        documentId: mapped.documentId,
        documentName: mapped.documentName,
        content: String(mapped.content || "").slice(0, 300),
        score: mapped.score,
      };
    });

    res.json({ answer, sources, question });
  } catch (err) {
    res.status(502).json({ error: "proxy_error", message: "Failed to reach backend" });
  }
});

export default router;
