import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { SearchPanel } from "./search-panel";

describe("SearchPanel", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("renders semantic search results", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => ({
          query: "semantic retrieval",
          results: [
            { score: 0.93, file_name: "alpha.txt" },
            { score: 0.75, file_name: "beta.txt" },
          ],
        }),
      }),
    );

    render(<SearchPanel />);

    fireEvent.click(screen.getByRole("button", { name: "Run Search" }));

    await waitFor(() => {
      expect(screen.getByText(/alpha.txt/)).toBeInTheDocument();
      expect(screen.getByText(/beta.txt/)).toBeInTheDocument();
      expect(screen.getByText("search complete")).toBeInTheDocument();
    });
  });
});
