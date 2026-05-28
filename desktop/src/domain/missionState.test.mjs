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

test("isActiveMissionStatus only accepts active Work states", () => {
  assert.equal(isActiveMissionStatus("running"), true);
  assert.equal(isActiveMissionStatus("waiting_input"), true);
  assert.equal(isActiveMissionStatus("completed"), false);
  assert.equal(isActiveMissionStatus("draft"), false);
});

function row(id, status, title, updatedAt = "2026-05-28T08:00:00Z") {
  return { project, mission: { id, status, title, updatedAt } };
}
