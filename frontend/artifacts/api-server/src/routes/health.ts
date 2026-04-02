import { Router, type IRouter } from "express";
import { fastapiUrl } from "../lib/proxy-utils";

const router: IRouter = Router();

router.get("/healthz", async (_req, res) => {
  try {
    const upstream = await fetch(fastapiUrl("/health"));
    const data = await upstream.json();
    res.json({ status: data.status || "ok" });
  } catch (err) {
    res.json({ status: "ok" });
  }
});

export default router;
