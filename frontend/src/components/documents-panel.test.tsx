import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { DocumentsPanel } from "./documents-panel";

describe("DocumentsPanel", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("uploads and refreshes document list", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({
          doc_id: "doc-1",
          file_name: "notes.txt",
          file_size_bytes: 12,
          ingested_at: "2026-01-01T00:00:00Z",
        }),
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({
          documents: [
            {
              doc_id: "doc-1",
              user_id: "user-1",
              file_name: "notes.txt",
              file_size_bytes: 12,
              ingested_at: "2026-01-01T00:00:00Z",
              file_type: "txt",
              file_path: "/tmp/notes.txt",
            },
          ],
        }),
      });

    vi.stubGlobal("fetch", fetchMock);

    render(<DocumentsPanel />);

    const fileInput = screen.getByLabelText("file") as HTMLInputElement;
    const file = new File(["study notes"], "notes.txt", { type: "text/plain" });
    fireEvent.change(fileInput, { target: { files: [file] } });

    fireEvent.click(screen.getByRole("button", { name: "Upload" }));

    await waitFor(() => {
      expect(screen.getByText("upload complete")).toBeInTheDocument();
      expect(screen.getByText("notes.txt")).toBeInTheDocument();
    });
  });
});
