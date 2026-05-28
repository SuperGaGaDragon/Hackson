/*
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
*/
import {
  CheckCircle2,
  Circle,
  Clock3,
  FileText,
  MessagesSquare,
  ListChecks,
  PanelTopOpen,
  PauseCircle,
  MessageSquareReply,
  RotateCw,
  Search,
  TriangleAlert,
  Wrench,
  ShieldCheck,
} from "lucide-react";

const actionLabels = {
  ask_user: "Ask",
  block_mission: "Block",
  delegate_agent: "Delegate",
  finish_mission: "Finish",
  inspect_product: "Inspect",
  mission_plan: "Plan",
  review_product: "Review",
  work_product: "Product",
  discuss_with_delegate: "Discuss",
  web_search: "Search",
  evaluate_product: "Evaluate",
};

export function eventView(event) {
  if (!event) {
    return {
      icon: Clock3,
      tone: "system",
      title: "Idle",
      detail: "",
      label: "",
      time: "",
      sequence: "",
    };
  }

  const tool = event.payload?.tool;
  const common = {
    detail: event.message || "",
    label: tool ? actionLabels[tool] || tool : "",
    sequence: event.sequence ? `#${event.sequence}` : "",
    time: formatEventTime(event),
  };

  switch (event.type) {
    case "MISSION_CREATED":
    case "MISSION_STARTED":
    case "MISSION_STOP_REQUESTED":
    case "MISSION_STOPPED":
      return { ...common, icon: Circle, tone: "system", title: event.title || "Mission" };
    case "MISSION_PLAN_UPDATED":
      return { ...common, icon: ListChecks, tone: "plan", title: event.title || "Plan" };
    case "MODEL_TURN_STARTED":
      return { ...common, icon: Clock3, tone: "model", title: "Thinking", detail: event.message || "Selecting tool" };
    case "MODEL_TURN_HEARTBEAT":
      return { ...common, icon: RotateCw, tone: "model", title: "Working", detail: event.message || "Still working" };
    case "MODEL_TURN_COMPLETED":
      return { ...common, icon: CheckCircle2, tone: "decision", title: "Tool selected", detail: event.message || tool || "" };
    case "MODEL_TURN_RETRYING":
      return { ...common, icon: RotateCw, tone: "retry", title: "Retrying" };
    case "MODEL_TURN_INVALID":
      return { ...common, icon: TriangleAlert, tone: "danger", title: "Invalid turn" };
    case "TOOL_CALLED":
      return {
        ...common,
        icon: Wrench,
        tone: "decision",
        title: actionLabels[tool] || event.title || "Tool",
        detail: event.message || tool || "",
      };
    case "PRODUCT_UPDATED":
      return { ...common, icon: FileText, tone: "product", title: event.title || "Product" };
    case "PRODUCT_INSPECTED":
      return { ...common, icon: Search, tone: "product", title: event.title || "Inspect" };
    case "WEB_SEARCH_COMPLETED":
      return { ...common, icon: Search, tone: "product", title: event.title || "Search" };
    case "WEB_SEARCH_FAILED":
      return { ...common, icon: TriangleAlert, tone: "danger", title: event.title || "Search failed" };
    case "EVALUATION_STARTED":
      return { ...common, icon: ShieldCheck, tone: "model", title: event.title || "Evaluation" };
    case "RELIABILITY_REPORTED":
      return { ...common, icon: ShieldCheck, tone: "review", title: event.title || "Reliability" };
    case "EVALUATION_FAILED":
      return { ...common, icon: TriangleAlert, tone: "danger", title: event.title || "Evaluation failed" };
    case "PRODUCT_REVIEWED":
      return { ...common, icon: ListChecks, tone: "review", title: event.title || "Review" };
    case "WORK_WINDOW_OPENED":
      return { ...common, icon: PanelTopOpen, tone: "window", title: event.title || "Window" };
    case "WORK_WINDOW_COMPLETED":
      return { ...common, icon: CheckCircle2, tone: "done", title: event.title || "Window done" };
    case "WORK_WINDOW_BLOCKED":
    case "MISSION_BLOCKED":
      return { ...common, icon: PauseCircle, tone: "retry", title: event.title || "Blocked" };
    case "WORK_WINDOW_FAILED":
    case "MISSION_FAILED":
      return { ...common, icon: TriangleAlert, tone: "danger", title: event.title || "Failed" };
    case "DISCUSSION_WINDOW_OPENED":
      return { ...common, icon: MessagesSquare, tone: "window", title: event.title || "Discussion" };
    case "DISCUSSION_WINDOW_COMPLETED":
      return { ...common, icon: CheckCircle2, tone: "done", title: event.title || "Discussion done" };
    case "DISCUSSION_WINDOW_BLOCKED":
      return { ...common, icon: PauseCircle, tone: "retry", title: event.title || "Discussion blocked" };
    case "DISCUSSION_WINDOW_FAILED":
      return { ...common, icon: TriangleAlert, tone: "danger", title: event.title || "Discussion failed" };
    case "USER_INPUT_REQUESTED":
      return { ...common, icon: MessageSquareReply, tone: "retry", title: event.title || "Input requested" };
    case "USER_INPUT_RECEIVED":
      return { ...common, icon: CheckCircle2, tone: "done", title: event.title || "Input received" };
    case "MISSION_PAUSED_RETRYABLE":
      return { ...common, icon: PauseCircle, tone: "retry", title: "Paused" };
    case "MISSION_COMPLETED":
      return { ...common, icon: CheckCircle2, tone: "done", title: "Done" };
    default:
      return { ...common, icon: Circle, tone: "system", title: event.title || event.type };
  }
}

export function formatEventTime(event) {
  const raw = event?.createdAt || event?.created_at;
  if (!raw) return "";
  const date = new Date(raw);
  if (Number.isNaN(date.getTime())) return "";
  return new Intl.DateTimeFormat(undefined, {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  }).format(date);
}

export function sortByCreatedAt(rows) {
  return [...rows].sort((a, b) => {
    const left = new Date(a.createdAt || a.created_at || 0).getTime();
    const right = new Date(b.createdAt || b.created_at || 0).getTime();
    if (left !== right) return left - right;
    return String(a.id || "").localeCompare(String(b.id || ""));
  });
}
