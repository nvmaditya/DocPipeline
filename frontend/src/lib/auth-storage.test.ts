import { afterEach, describe, expect, it } from "vitest";

import { clearStoredToken, getStoredToken, setStoredToken } from "./auth-storage";

describe("auth-storage", () => {
  afterEach(() => {
    clearStoredToken();
  });

  it("stores and clears token", () => {
    expect(getStoredToken()).toBeNull();

    setStoredToken("dev-token-123");
    expect(getStoredToken()).toBe("dev-token-123");

    clearStoredToken();
    expect(getStoredToken()).toBeNull();
  });
});
