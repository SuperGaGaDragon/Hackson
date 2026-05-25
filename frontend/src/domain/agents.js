/*
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
*/
export const AGENT_BY_SLOT = {
  agent_1: {
    slot: "agent_1",
    short: "A1",
    name: "Nora",
    color: "teal",
    voice: "precise",
  },
  agent_2: {
    slot: "agent_2",
    short: "A2",
    name: "Vale",
    color: "amber",
    voice: "sharp",
  },
};

export const AGENTS = Object.values(AGENT_BY_SLOT);

export function resolveAgent(senderSlot) {
  return AGENT_BY_SLOT[senderSlot] || null;
}
