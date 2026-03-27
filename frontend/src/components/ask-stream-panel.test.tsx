import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { AskStreamPanel } from "./ask-stream-panel";

describe("AskStreamPanel", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("renders meta/token/done SSE events", async () => {
    const payload =
      'data: {"type":"meta","query":"q","sources":["guide.pdf"]}\n\n' +
      'data: {"type":"token","content":"Analyzing"}\n\n' +
      'data: {"type":"done","answer":"Analyzing"}\n\n';

    const stream = new ReadableStream<Uint8Array>({
      start(controller) {
        controller.enqueue(new TextEncoder().encode(payload));
        controller.close();
      },
    });

    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        body: stream,
      }),
    );

    render(<AskStreamPanel />);

    fireEvent.click(screen.getByRole("button", { name: "Stream Answer" }));

    await waitFor(() => {
      expect(screen.getByText("guide.pdf")).toBeInTheDocument();
      expect(screen.getAllByText("Analyzing").length).toBeGreaterThanOrEqual(2);
      expect(screen.getByText("stream complete")).toBeInTheDocument();
    });
  });
});
