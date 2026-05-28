/*
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
*/
import catIdle1 from "../assets/cat_idle1_cutout.png";
import catIdle2 from "../assets/cat_idle2_cutout.png";
import catSleep from "../assets/cat_sleep_cutout.png";
import catWalk1 from "../assets/cat_walk1_cutout.png";

export const petStates = {
  stand: {
    label: "Stand",
    shortLabel: "Here",
    line: "Here",
    frames: [catIdle1, catIdle2],
    frameCadenceMs: 820,
    nextAfterMs: 12000,
    nextState: "walk",
    mood: "calm",
    nudgePx: 0,
  },
  walk: {
    label: "Walk",
    shortLabel: "Walk",
    line: "Walking",
    frames: [catWalk1],
    frameCadenceMs: 900,
    nextAfterMs: 6500,
    nextState: "stand",
    mood: "active",
    nudgePx: 14,
  },
  sleep: {
    label: "Sleep",
    shortLabel: "Nap",
    line: "Napping",
    frames: [catSleep],
    frameCadenceMs: 1200,
    nextAfterMs: 14000,
    nextState: "stand",
    mood: "soft",
    nudgePx: 0,
  },
  siteIdle: {
    label: "Ready",
    shortLabel: "Site",
    line: "Watching site",
    frames: [catIdle1, catIdle2],
    frameCadenceMs: 900,
    nextAfterMs: 16000,
    nextState: "siteIdle",
    mood: "site",
    nudgePx: 0,
  },
  siteActive: {
    label: "Working",
    shortLabel: "Work",
    line: "Site working",
    frames: [catWalk1],
    frameCadenceMs: 800,
    nextAfterMs: 12000,
    nextState: "siteActive",
    mood: "active",
    nudgePx: 10,
  },
  siteWaiting: {
    label: "Waiting",
    shortLabel: "Wait",
    line: "Needs you",
    frames: [catIdle1, catIdle2],
    frameCadenceMs: 640,
    nextAfterMs: 12000,
    nextState: "siteWaiting",
    mood: "waiting",
    nudgePx: 0,
  },
  sitePaused: {
    label: "Paused",
    shortLabel: "Pause",
    line: "Paused",
    frames: [catSleep],
    frameCadenceMs: 1200,
    nextAfterMs: 12000,
    nextState: "sitePaused",
    mood: "soft",
    nudgePx: 0,
  },
  siteDone: {
    label: "Done",
    shortLabel: "Done",
    line: "Done",
    frames: [catIdle2, catIdle1],
    frameCadenceMs: 700,
    nextAfterMs: 12000,
    nextState: "siteDone",
    mood: "done",
    nudgePx: 0,
  },
  siteFailed: {
    label: "Failed",
    shortLabel: "Fail",
    line: "Failed",
    frames: [catIdle1],
    frameCadenceMs: 1200,
    nextAfterMs: 12000,
    nextState: "siteFailed",
    mood: "failed",
    nudgePx: 0,
  },
  siteOffline: {
    label: "Offline",
    shortLabel: "Off",
    line: "Offline",
    frames: [catSleep],
    frameCadenceMs: 1400,
    nextAfterMs: 12000,
    nextState: "siteOffline",
    mood: "offline",
    nudgePx: 0,
  },
};

export const petStateOrder = ["stand", "walk", "sleep"];

export const sitePetStateByTone = {
  active: "siteActive",
  done: "siteDone",
  failed: "siteFailed",
  idle: "siteIdle",
  offline: "siteOffline",
  paused: "sitePaused",
  retrying: "siteActive",
  waiting: "siteWaiting",
};

export function getPetState(state) {
  return petStates[state] || petStates.stand;
}
