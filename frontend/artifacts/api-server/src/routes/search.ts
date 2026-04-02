import { Router, type IRouter } from "express";
import { fastapiUrl, forwardAuth, mapSearchResult } from "../lib/proxy-utils";

const router: IRouter = Router();

router.post("/search", async (req, res): Promise<void> => {
  try {
    const { query, limit = 10, documentIds, databaseId } = req.body;

    // Build query params for FastAPI — include database_id if provided (community scoping)
    const searchParams: Record<string, string> = {};
    if (databaseId) searchParams["database_id"] = databaseId;
    const qs = new URLSearchParams(searchParams).toString();
    const suffix = qs ? `?${qs}` : "";

    const upstream = await fetch(fastapiUrl(`/api/v1/search/semantic${suffix}`), {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...forwardAuth(req),
      },
      body: JSON.stringify({ query, top_k: limit }),
    });

    if (!upstream.ok) {
      const err = await upstream.json().catch(() => ({}));
      res.status(upstream.status).json(err);
      return;
    }

    const data = (await upstream.json()) as { query: string; results: Record<string, unknown>[] };
    const results = (data.results || []).map(mapSearchResult);

    res.json({
      results,
      query: data.query || query,
      total: results.length,
    });
  } catch (err) {
    res.status(502).json({ error: "proxy_error", message: "Failed to reach backend" });
  }
});

export default router;
