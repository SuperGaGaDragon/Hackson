/*
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
*/
import assert from "node:assert/strict";
import { test } from "node:test";

import {
  chooseBestMission,
  deriveSitePetState,
  deriveProgressSummary,
  isActiveMissionStatus,
  summarizeActiveMissions,
} from "./missionState.js";

const project = { id: "project_1", name: "Novel" };

test("chooseBestMission ignores inactive missions", () => {
  const rows = [
    row("draft_1", "draft", "Draft work"),
    row("done_1", "completed", "Done work"),
    row("failed_1", "failed", "Failed work"),
  ];

  assert.equal(chooseBestMission(rows), null);
  assert.deepEqual(summarizeActiveMissions(rows), { activeCount: 0, primaryMissionId: "", primaryTitle: "" });
});

test("chooseBestMission ignores stale selection and picks most active mission", () => {
  const rows = [
    row("run_1", "running", "Primary", "2026-05-28T10:00:00Z"),
    row("wait_1", "waiting_input", "Needs user", "2026-05-28T11:00:00Z"),
  ];

  assert.equal(chooseBestMission(rows, "wait_1").mission.id, "run_1");
  assert.equal(summarizeActiveMissions(rows).primaryTitle, "Primary");
});

test("chooseBestMission ranks active status then recency", () => {
  const rows = [
    row("blocked_1", "blocked", "Blocked", "2026-05-28T12:00:00Z"),
    row("run_old", "running", "Old run", "2026-05-28T09:00:00Z"),
    row("run_new", "running", "New run", "2026-05-28T10:00:00Z"),
  ];

  assert.equal(chooseBestMission(rows).mission.id, "run_new");
  assert.equal(summarizeActiveMissions(rows).activeCount, 3);
});

test("chooseBestMission lets a new running mission replace an older paused watch", () => {
  const rows = [
    row("paused_newer", "paused_retryable", "Old paused", "2026-05-28T12:00:00Z"),
    row("running_older", "running", "New running", "2026-05-28T11:00:00Z"),
  ];

  assert.equal(chooseBestMission(rows, "paused_newer").mission.id, "running_older");
  assert.equal(summarizeActiveMissions(rows).primaryTitle, "New running");
});

test("deriveSitePetState shows no active work without selected mission", () => {
  const state = deriveSitePetState({ authenticated: true, selectedMission: null });

  assert.equal(state.key, "noActiveWork");
  assert.equal(state.line, "No active work");
});

test("deriveSitePetState includes mission title and count for multiple active missions", () => {
  const state = deriveSitePetState({
    activeSummary: { activeCount: 2, primaryMissionId: "run_1", primaryTitle: "Launch plan" },
    authenticated: true,
    selectedMission: { id: "run_1", status: "running", title: "Launch plan" },
    missionDetail: { mission: { id: "run_1", status: "running", title: "Launch plan" }, workWindows: [] },
    events: [],
  });

  assert.equal(state.key, "working");
  assert.equal(state.line, "[Launch plan] +1");
});

test("deriveSitePetState uses English system fallback copy", () => {
  const cases = [
    {
      expected: "Site offline",
      input: { authenticated: true, error: "Site offline", selectedMission: null },
    },
    {
      expected: "Sign in",
      input: { authenticated: false, selectedMission: null },
    },
    {
      expected: "Task failed",
      input: {
        authenticated: true,
        selectedMission: { id: "failed_1", status: "failed", title: "" },
        missionDetail: { mission: { id: "failed_1", status: "failed", title: "" }, workWindows: [] },
        events: [],
      },
    },
    {
      expected: "Needs you",
      input: {
        authenticated: true,
        selectedMission: { id: "wait_1", status: "waiting_input", title: "" },
        missionDetail: { mission: { id: "wait_1", status: "waiting_input", title: "" }, workWindows: [] },
        events: [],
      },
    },
    {
      expected: "Task paused",
      input: {
        authenticated: true,
        selectedMission: { id: "paused_1", status: "paused_retryable", title: "" },
        missionDetail: { mission: { id: "paused_1", status: "paused_retryable", title: "" }, workWindows: [] },
        events: [],
      },
    },
    {
      expected: "Running",
      input: {
        authenticated: true,
        selectedMission: { id: "run_1", status: "running", title: "" },
        missionDetail: { mission: { id: "run_1", status: "running", title: "" }, workWindows: [] },
        events: [],
      },
    },
  ];

  for (const item of cases) {
    assert.equal(deriveSitePetState(item.input).line, item.expected);
  }
});

test("deriveProgressSummary shows current mission progress rows", () => {
  const summary = deriveProgressSummary({
    mission: { id: "run_1", status: "running", title: "Launch plan" },
    state: { label: "Working", line: "[Launch plan]" },
    events: [
      event("e1", 1, "MISSION_CREATED", "Mission created", "Launch plan", "2026-05-28T10:00:00Z"),
      event("e2", 2, "MODEL_TURN_STARTED", "Thinking", "Selecting next tool.", "2026-05-28T10:01:00Z"),
      event("e3", 3, "TOOL_CALLED", "Delegate", "A1 started.", "2026-05-28T10:02:00Z"),
      event("e4", 4, "PRODUCT_UPDATED", "Product", "Draft updated.", "2026-05-28T10:03:00Z"),
    ],
  });

  assert.equal(summary.title, "Launch plan");
  assert.equal(summary.status, "Working");
  assert.equal(summary.detail, "[Launch plan]");
  assert.deepEqual(
    summary.rows.map((row) => row.title),
    ["Product", "Delegate", "Thinking", "Mission created"],
  );
  assert.equal(summary.rows.length, 4);
  assert.equal(summary.rows[0].sequence, "#4");
  assert.equal(summary.rows[0].detail, "Draft updated.");
});

test("deriveProgressSummary has a quiet empty state", () => {
  const summary = deriveProgressSummary({
    mission: null,
    state: { label: "No work", line: "No active work" },
    events: [],
  });

  assert.equal(summary.title, "No active work");
  assert.equal(summary.status, "No work");
  assert.equal(summary.rows.length, 0);
  assert.equal(summary.empty, "No progress yet");
});

test("isActiveMissionStatus only accepts active Work states", () => {
  assert.equal(isActiveMissionStatus("running"), true);
  assert.equal(isActiveMissionStatus("waiting_input"), true);
  assert.equal(isActiveMissionStatus("completed"), false);
  assert.equal(isActiveMissionStatus("draft"), false);
});

function row(id, status, title, updatedAt = "2026-05-28T08:00:00Z") {
  return { project, mission: { id, status, title, updatedAt } };
}

function event(id, sequence, type, title, message, createdAt) {
  return {
    id,
    sequence,
    type,
    title,
    message,
    createdAt,
    payload: {},
  };
}
