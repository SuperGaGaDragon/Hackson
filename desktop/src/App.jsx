/*
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
*/
import { useEffect, useMemo, useState } from "react";
import { invoke } from "@tauri-apps/api/core";
import { getApiSourceId, getSiteUrl, getToken, resolveApiSource } from "./api/client";
import { claimDesktopHandoff, getCurrentUser } from "./api/users";
import { getMission, listMissionEvents, listProjectMissions, listProjects } from "./api/work";
import {
  chooseBestMission,
  deriveSitePetState,
  isActiveMissionStatus,
  latestSequence,
  summarizeActiveMissions,
} from "./domain/missionState";
import PetWindow from "./features/pet/PetWindow";

const SELECTED_PROJECT_KEY = "hackson_desktop_pet_project_id";
const SELECTED_MISSION_KEY = "hackson_desktop_pet_mission_id";

function App() {
  const [apiSourceId] = useState(() => getApiSourceId());
  const [resolvedSourceId, setResolvedSourceId] = useState("");
  const [user, setUser] = useState(null);
  const [projects, setProjects] = useState([]);
  const [missions, setMissions] = useState([]);
  const [selectedProjectId, setSelectedProjectId] = useState("");
  const [selectedMissionId, setSelectedMissionId] = useState("");
  const [missionDetail, setMissionDetail] = useState(null);
  const [events, setEvents] = useState([]);
  const [watchLabel, setWatchLabel] = useState("");
  const [activeSummary, setActiveSummary] = useState({ activeCount: 0, primaryTitle: "", primaryMissionId: "" });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [handoffCode, setHandoffCode] = useState("");

  const selectedMission = useMemo(
    () => missions.find((mission) => mission.id === selectedMissionId) || missionDetail?.mission || null,
    [missionDetail, missions, selectedMissionId],
  );
  const siteState = useMemo(
    () =>
      deriveSitePetState({
        activeSummary,
        authenticated: Boolean(user),
        selectedMission,
        missionDetail,
        events,
        error: handoffCode ? "" : error,
      }),
    [activeSummary, error, events, handoffCode, missionDetail, selectedMission, user],
  );
  const displayState = handoffCode
    ? { key: "linking", label: "Login", line: "浏览器登录。", tone: "waiting" }
    : siteState;

  useEffect(() => {
    let cancelled = false;
    async function connectSource() {
      setBusy(true);
      setError("");
      resetSessionData();
      try {
        const nextResolvedSourceId = await resolveApiSource(apiSourceId);
        if (cancelled) return;
        setResolvedSourceId(nextResolvedSourceId);
        const savedProjectId = localStorage.getItem(sourceStorageKey(SELECTED_PROJECT_KEY, nextResolvedSourceId)) || "";
        const savedMissionId = localStorage.getItem(sourceStorageKey(SELECTED_MISSION_KEY, nextResolvedSourceId)) || "";
        setSelectedProjectId(savedProjectId);
        setSelectedMissionId(savedMissionId);
        if (getToken(nextResolvedSourceId)) {
          await bootstrap(nextResolvedSourceId, savedMissionId, false);
        }
      } catch (err) {
        if (!cancelled) {
          setResolvedSourceId("");
          setError(err.message || "Site offline");
        }
      } finally {
        if (!cancelled) setBusy(false);
      }
    }
    connectSource();
    return () => {
      cancelled = true;
    };
  }, [apiSourceId]);

  useEffect(() => {
    if (!user || !selectedMissionId || !resolvedSourceId) return undefined;
    let cancelled = false;
    async function poll() {
      try {
        const detail = await getMission(selectedMissionId, requestOptions(resolvedSourceId));
        if (cancelled) return;
        const nextEvents = await listMissionEvents(selectedMissionId, latestSequence(events), requestOptions(resolvedSourceId));
        if (cancelled) return;
        setMissionDetail(detail);
        if (nextEvents.length > 0) setEvents((current) => mergeEvents(current, nextEvents));
        setError("");
        if (!isActiveMissionStatus(detail.mission?.status)) {
          await scanAndSelectMission("", resolvedSourceId, { manageBusy: false });
        }
      } catch (err) {
        if (!cancelled) setError(err.message || "Site offline");
      }
    }
    poll();
    const timer = window.setInterval(poll, shouldFastPoll(missionDetail?.mission?.status) ? 2500 : 15000);
    return () => {
      cancelled = true;
      window.clearInterval(timer);
    };
  }, [apiSourceId, events, missionDetail?.mission?.status, resolvedSourceId, selectedMissionId, user]);

  useEffect(() => {
    if (!user || !resolvedSourceId) return undefined;
    let cancelled = false;
    let scanning = false;
    async function rescan() {
      if (cancelled || scanning) return;
      scanning = true;
      try {
        await scanAndSelectMission("", resolvedSourceId, { manageBusy: false });
      } finally {
        scanning = false;
      }
    }
    const timer = window.setInterval(() => {
      rescan();
    }, 10000);
    return () => {
      cancelled = true;
      window.clearInterval(timer);
    };
  }, [apiSourceId, missionDetail?.mission?.id, resolvedSourceId, selectedMissionId, user]);

  async function bootstrap(sourceId = resolvedSourceId, preferredMissionId = selectedMissionId, manageBusy = true) {
    if (!sourceId) return;
    if (manageBusy) setBusy(true);
    setError("");
    try {
      const currentUser = await getCurrentUser(requestOptions(sourceId));
      setUser(currentUser);
      await scanAndSelectMission(preferredMissionId, sourceId, { manageBusy: false });
    } catch (err) {
      setError(err.message || "Login expired");
    } finally {
      if (manageBusy) setBusy(false);
    }
  }

  useEffect(() => {
    if (!handoffCode || user || !resolvedSourceId) return undefined;
    let cancelled = false;
    async function claim() {
      try {
        const data = await claimDesktopHandoff(handoffCode, requestOptions(resolvedSourceId));
        if (cancelled || data.status !== "authorized") return;
        setHandoffCode("");
        setUser(data.user);
        await scanAndSelectMission(selectedMissionId, resolvedSourceId);
      } catch (err) {
        if (!cancelled) setError(err.message || "Login failed");
      }
    }
    claim();
    const timer = window.setInterval(claim, 1600);
    return () => {
      cancelled = true;
      window.clearInterval(timer);
    };
  }, [handoffCode, resolvedSourceId, selectedMissionId, user]);

  async function startBrowserLogin() {
    setBusy(true);
    setError("");
    try {
      const sourceId = resolvedSourceId || (await resolveApiSource(apiSourceId));
      setResolvedSourceId(sourceId);
      const code = createDesktopHandoffCode();
      setHandoffCode(code);
      await invoke("open_site", {
        path: `/?desktopAuth=${encodeURIComponent(code)}`,
        baseUrl: getSiteUrl(apiSourceId, sourceId),
      });
    } catch (err) {
      setError(err.message || "Login failed");
    } finally {
      setBusy(false);
    }
  }

  async function scanAndSelectMission(preferredMissionId = selectedMissionId, sourceId = resolvedSourceId, options = {}) {
    if (!sourceId) return;
    const manageBusy = options.manageBusy !== false;
    if (manageBusy) setBusy(true);
    setError("");
    try {
      const request = requestOptions(sourceId);
      const projectRows = await listProjects(request);
      setProjects(projectRows);
      const candidates = [];
      for (const project of projectRows) {
        const missionRows = await listProjectMissions(project.id, request);
        for (const mission of missionRows) candidates.push({ project, mission });
      }
      const nextSummary = summarizeActiveMissions(candidates);
      setActiveSummary(nextSummary);
      const best = chooseBestMission(candidates, preferredMissionId);
      if (!best) {
        setMissions([]);
        setSelectedProjectId("");
        setSelectedMissionId("");
        setMissionDetail(null);
        setEvents([]);
        setWatchLabel("");
        localStorage.removeItem(sourceStorageKey(SELECTED_PROJECT_KEY, sourceId));
        localStorage.removeItem(sourceStorageKey(SELECTED_MISSION_KEY, sourceId));
        return;
      }
      setSelectedProjectId(best.project.id);
      localStorage.setItem(sourceStorageKey(SELECTED_PROJECT_KEY, sourceId), best.project.id);
      const projectMissions = candidates
        .filter((candidate) => candidate.project.id === best.project.id)
        .map((candidate) => candidate.mission);
      setMissions(projectMissions);
      setWatchLabel(formatWatchLabel(best.project.name, nextSummary));
      if (best.mission.id === selectedMissionId && missionDetail?.mission?.id === best.mission.id) {
        return;
      }
      await selectMission(best.mission.id, { preserveProject: true, sourceId });
    } catch (err) {
      setError(err.message || "Scan failed");
    } finally {
      if (manageBusy) setBusy(false);
    }
  }

  async function selectProject(projectId, preferredMissionId = "", sourceId = resolvedSourceId) {
    if (!sourceId) return;
    try {
      setSelectedProjectId(projectId);
      localStorage.setItem(sourceStorageKey(SELECTED_PROJECT_KEY, sourceId), projectId);
      const missionRows = projectId ? await listProjectMissions(projectId, requestOptions(sourceId)) : [];
      setMissions(missionRows);
      const project = projects.find((row) => row.id === projectId) || { id: projectId, name: "" };
      const candidates = missionRows.map((mission) => ({ project, mission }));
      const nextSummary = summarizeActiveMissions(candidates);
      setActiveSummary(nextSummary);
      const best = chooseBestMission(candidates, preferredMissionId);
      const nextMissionId = best?.mission.id || "";
      const selected = missionRows.find((mission) => mission.id === nextMissionId);
      if (selected) setWatchLabel(formatWatchLabel(project.name, nextSummary));
      if (nextMissionId) {
        await selectMission(nextMissionId, { preserveProject: true, sourceId });
      } else {
        setSelectedMissionId("");
        setMissionDetail(null);
        setEvents([]);
        setWatchLabel("");
        setActiveSummary({ activeCount: 0, primaryTitle: "", primaryMissionId: "" });
        localStorage.removeItem(sourceStorageKey(SELECTED_MISSION_KEY, sourceId));
      }
    } catch (err) {
      setError(err.message || "Project failed");
    }
  }

  async function selectMission(missionId, options = {}) {
    const sourceId = options.sourceId || resolvedSourceId;
    if (!sourceId) return;
    try {
      setSelectedMissionId(missionId);
      localStorage.setItem(sourceStorageKey(SELECTED_MISSION_KEY, sourceId), missionId);
      setEvents([]);
      if (!missionId) {
        setMissionDetail(null);
        return;
      }
      const detail = await getMission(missionId, requestOptions(sourceId));
      setMissionDetail(detail);
      setEvents(detail.events || []);
      if (!options.preserveProject) setWatchLabel(detail.mission?.title || "");
    } catch (err) {
      setError(err.message || "Mission failed");
    }
  }

  function resetSessionData() {
    setUser(null);
    setProjects([]);
    setMissions([]);
    setSelectedProjectId("");
    setSelectedMissionId("");
    setMissionDetail(null);
    setEvents([]);
    setWatchLabel("");
    setActiveSummary({ activeCount: 0, primaryTitle: "", primaryMissionId: "" });
  }

  async function openSite() {
    if (!user) {
      await startBrowserLogin();
      return;
    }
    await invoke("open_site", { path: "/", baseUrl: getSiteUrl(apiSourceId, resolvedSourceId) });
  }

  function requestOptions(sourceId = resolvedSourceId) {
    return { sourceId: apiSourceId, resolvedSourceId: sourceId };
  }

  return (
    <>
      <PetWindow busy={busy} onOpenSite={openSite} siteState={displayState} />
    </>
  );
}

function shouldFastPoll(status) {
  return ["running", "stopping", "waiting_input"].includes(status);
}

function mergeEvents(current, nextEvents) {
  const map = new Map(current.map((event) => [event.id, event]));
  for (const event of nextEvents) map.set(event.id, event);
  return Array.from(map.values()).sort((a, b) => Number(a.sequence || 0) - Number(b.sequence || 0));
}

function sourceStorageKey(key, sourceId) {
  return `${key}_${sourceId}`;
}

function formatWatchLabel(projectName, summary) {
  if (!summary?.activeCount) return "";
  const suffix = summary.activeCount > 1 ? ` +${summary.activeCount - 1}` : "";
  return `${projectName} · ${summary.primaryTitle}${suffix}`;
}

function createDesktopHandoffCode() {
  const bytes = new Uint8Array(24);
  window.crypto.getRandomValues(bytes);
  return Array.from(bytes, (byte) => byte.toString(36).padStart(2, "0")).join("");
}

export default App;
