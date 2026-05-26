/*
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
*/
export const FALLBACK_AGENT_BY_SLOT = {
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

export const FALLBACK_AGENTS = Object.values(FALLBACK_AGENT_BY_SLOT);

export function normalizeAgents(agents) {
  const source = Array.isArray(agents) && agents.length ? agents : FALLBACK_AGENTS;
  return source.map(normalizeAgent);
}

export function agentsToMap(agents) {
  return Object.fromEntries(normalizeAgents(agents).map((agent) => [agent.slot, agent]));
}

export function resolveAgent(senderSlot, agentBySlot = FALLBACK_AGENT_BY_SLOT) {
  return agentBySlot[senderSlot] || FALLBACK_AGENT_BY_SLOT[senderSlot] || null;
}

export function nextAgentSlot(currentSlot, agents) {
  const slots = normalizeAgents(agents).map((agent) => agent.slot);
  const currentIndex = slots.indexOf(currentSlot);
  if (currentIndex === -1) return slots[0] || "agent_1";
  return slots[(currentIndex + 1) % slots.length] || "agent_1";
}

function normalizeAgent(agent) {
  const fallback = FALLBACK_AGENT_BY_SLOT[agent?.slot] || {};
  return {
    slot: agent?.slot || fallback.slot || "agent_1",
    short: agent?.short || fallback.short || "A",
    name: agent?.name || fallback.name || "Agent",
    color: agent?.color || fallback.color || "teal",
    voice: agent?.voice || fallback.voice || "ready",
  };
}
