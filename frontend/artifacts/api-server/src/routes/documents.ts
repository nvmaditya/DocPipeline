import { Router, type IRouter } from "express";
import multer from "multer";
import { fastapiUrl, forwardAuth, mapDocument } from "../lib/proxy-utils";

const router: IRouter = Router();

const upload = multer({
  storage: multer.memoryStorage(),
  limits: { fileSize: 50 * 1024 * 1024 },
});

router.get("/documents", async (req, res): Promise<void> => {
  let upstream: Response | undefined;
  try {
    upstream = await fetch(fastapiUrl("/api/v1/docs/list"), {
      headers: { ...forwardAuth(req) },
    });
  } catch {
    res.status(502).json({ error: "proxy_error", message: "Cannot reach backend at " + fastapiUrl("") });
    return;
  }

  if (!upstream.ok) {
    const body = await upstream.text().catch(() => "{}");
    let parsed: unknown;
    try { parsed = JSON.parse(body); } catch { parsed = { detail: body }; }
    res.status(upstream.status).json(parsed);
    return;
  }

  const data = (await upstream.json()) as { documents: Record<string, unknown>[] };
  const documents = (data.documents || []).map(mapDocument);
  res.json({ documents, total: documents.length });
});

router.get("/documents/:documentId", async (req, res): Promise<void> => {
  let upstream: Response | undefined;
  try {
    upstream = await fetch(fastapiUrl(`/api/v1/docs/${req.params.documentId}`), {
      headers: { ...forwardAuth(req) },
    });
  } catch {
    res.status(502).json({ error: "proxy_error", message: "Cannot reach backend" });
    return;
  }

  if (!upstream.ok) {
    const body = await upstream.text().catch(() => "{}");
    let parsed: unknown;
    try { parsed = JSON.parse(body); } catch { parsed = { detail: body }; }
    res.status(upstream.status).json(parsed);
    return;
  }

  const raw = (await upstream.json()) as Record<string, unknown>;
  res.json(mapDocument(raw));
});

router.delete("/documents/:documentId", async (req, res): Promise<void> => {
  let upstream: Response | undefined;
  try {
    upstream = await fetch(fastapiUrl(`/api/v1/docs/${req.params.documentId}`), {
      method: "DELETE",
      headers: { ...forwardAuth(req) },
    });
  } catch {
    res.status(502).json({ error: "proxy_error", message: "Cannot reach backend" });
    return;
  }

  if (!upstream.ok) {
    const body = await upstream.text().catch(() => "{}");
    let parsed: unknown;
    try { parsed = JSON.parse(body); } catch { parsed = { detail: body }; }
    res.status(upstream.status).json(parsed);
    return;
  }

  res.json({ success: true, message: "Document deleted" });
});

router.post("/documents/upload", upload.single("file"), async (req, res): Promise<void> => {
  if (!req.file) {
    res.status(400).json({ error: "no_file", message: "No file uploaded" });
    return;
  }

  const formData = new FormData();
  const blob = new Blob([req.file.buffer], { type: req.file.mimetype });
  formData.append("file", blob, req.file.originalname);

  let upstream: Response | undefined;
  try {
    upstream = await fetch(fastapiUrl("/api/v1/docs/upload"), {
      method: "POST",
      headers: { ...forwardAuth(req) },
      body: formData,
    });
  } catch {
    res.status(502).json({ error: "proxy_error", message: "Cannot reach backend" });
    return;
  }

  if (!upstream.ok) {
    const body = await upstream.text().catch(() => "{}");
    let parsed: unknown;
    try { parsed = JSON.parse(body); } catch { parsed = { detail: body }; }
    res.status(upstream.status).json(parsed);
    return;
  }

  const raw = (await upstream.json()) as Record<string, unknown>;
  res.status(201).json(mapDocument(raw));
});

export default router;
