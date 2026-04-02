import { Router, type IRouter } from "express";
import { fastapiUrl, forwardAuth } from "../lib/proxy-utils";

const router: IRouter = Router();

router.post("/auth/register", async (req, res): Promise<void> => {
  try {
    const upstream = await fetch(fastapiUrl("/api/v1/auth/register"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(req.body),
    });
    const data = await upstream.json();
    res.status(upstream.status).json(data);
  } catch (err) {
    res.status(502).json({ error: "proxy_error", message: "Failed to reach backend" });
  }
});

router.post("/auth/login", async (req, res): Promise<void> => {
  try {
    const upstream = await fetch(fastapiUrl("/api/v1/auth/login"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(req.body),
    });
    const data = await upstream.json();
    res.status(upstream.status).json(data);
  } catch (err) {
    res.status(502).json({ error: "proxy_error", message: "Failed to reach backend" });
  }
});

router.post("/auth/logout", async (req, res): Promise<void> => {
  try {
    const upstream = await fetch(fastapiUrl("/api/v1/auth/logout"), {
      method: "POST",
      headers: { ...forwardAuth(req) },
    });
    const data = await upstream.json();
    res.status(upstream.status).json(data);
  } catch (err) {
    res.status(502).json({ error: "proxy_error", message: "Failed to reach backend" });
  }
});

router.get("/auth/me", async (req, res): Promise<void> => {
  try {
    const upstream = await fetch(fastapiUrl("/api/v1/auth/me"), {
      headers: { ...forwardAuth(req) },
    });
    const data = await upstream.json();
    res.status(upstream.status).json(data);
  } catch (err) {
    res.status(502).json({ error: "proxy_error", message: "Failed to reach backend" });
  }
});

export default router;
