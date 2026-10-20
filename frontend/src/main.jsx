/*
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-10-20
Last Modified by: Codex
*/
import React from "react";
import { createRoot } from "react-dom/client";
import "@fontsource-variable/instrument-sans";
import "@fontsource/ibm-plex-mono/latin-400.css";
import "@fontsource/ibm-plex-mono/latin-500.css";
import App from "./App.jsx";
import "./styles.css";
import "./light-theme.css";

createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
