import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { AuthPanel } from "./auth-panel";

describe("AuthPanel", () => {
  afterEach(() => {
    vi.restoreAllMocks();
    localStorage.removeItem("docpipe_access_token");
  });

  it("logs in and stores bearer token", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => ({ access_token: "dev-token-u1", token_type: "bearer" }),
      }),
    );

    render(<AuthPanel />);

    fireEvent.click(screen.getByRole("button", { name: "Login" }));

    await waitFor(() => {
      expect(screen.getByTestId("auth-status")).toHaveTextContent("login complete");
      expect(localStorage.getItem("docpipe_access_token")).toBe("dev-token-u1");
    });
  });
});
