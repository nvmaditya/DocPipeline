import { defineConfig } from "vitest/config";
import { fileURLToPath } from "node:url";

export default defineConfig({
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  test: {
    environment: "jsdom",
    setupFiles: ["./vitest.setup.ts"],
    include: ["src/**/*.test.ts", "src/**/*.test.tsx"],
    coverage: {
      provider: "v8",
      reporter: ["text", "html"],
      include: [
        "src/lib/api-client.ts",
        "src/lib/auth-storage.ts",
        "src/components/**/*.tsx"
      ],
      thresholds: {
        lines: 80,
        branches: 70,
        functions: 70,
        statements: 80
      }
    }
  }
});
