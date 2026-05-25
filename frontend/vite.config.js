/*
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
*/
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const proxyTarget =
  process.env.VITE_API_PROXY_TARGET || process.env.VITE_API_BASE_URL || "http://127.0.0.1:8101";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": {
        target: proxyTarget,
        changeOrigin: true,
      },
    },
  },
});
