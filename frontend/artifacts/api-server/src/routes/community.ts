import { Router, type IRouter } from "express";
import { fastapiUrl, forwardAuth } from "../lib/proxy-utils";

const router: IRouter = Router();

router.get("/community/databases", async (req, res): Promise<void> => {
  try {
    const upstream = await fetch(fastapiUrl("/api/v1/community/databases"), {
      headers: { ...forwardAuth(req) },
    });
    if (!upstream.ok) {
      const err = await upstream.json().catch(() => ({}));
      res.status(upstream.status).json(err);
      return;
    }
    const data = await upstream.json();
    res.json(data);
  } catch (err) {
    res.status(502).json({ error: "proxy_error", message: "Failed to reach backend" });
  }
});

router.post("/community/modules", async (req, res): Promise<void> => {
  try {
    const upstream = await fetch(fastapiUrl("/api/v1/community/modules"), {
      method: "POST",
      headers: { ...forwardAuth(req), "Content-Type": "application/json" },
      body: JSON.stringify(req.body),
    });
    if (!upstream.ok) {
      const err = await upstream.json().catch(() => ({}));
      res.status(upstream.status).json(err);
      return;
    }
    const data = await upstream.json();
    res.json(data);
  } catch (err) {
    res.status(502).json({ error: "proxy_error", message: "Failed to reach backend" });
  }
});

router.get("/community/databases/:id/topics", async (req, res): Promise<void> => {
  try {
    const upstream = await fetch(
      fastapiUrl(`/api/v1/community/databases/${req.params.id}/topics`),
      { headers: { ...forwardAuth(req) } },
    );
    if (!upstream.ok) {
      const err = await upstream.json().catch(() => ({}));
      res.status(upstream.status).json(err);
      return;
    }
    const data = await upstream.json();
    res.json(data);
  } catch (err) {
    res.status(502).json({ error: "proxy_error", message: "Failed to reach backend" });
  }
});

export default router;
