import { Router, type IRouter } from "express";
import { fastapiUrl, forwardAuth } from "../lib/proxy-utils";

const router: IRouter = Router();

router.post("/study/generate", async (req, res): Promise<void> => {
  try {
    const upstream = await fetch(fastapiUrl("/api/v1/study/generate"), {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...forwardAuth(req),
      },
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

export default router;
