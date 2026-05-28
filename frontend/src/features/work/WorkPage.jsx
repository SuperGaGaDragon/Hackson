/*
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
*/
import { useEffect, useMemo, useRef, useState } from "react";
import {
  answerMission,
  continueMissionFollowUp,
  createMission,
  createProject,
  evaluateMission,
  getMission,
  listMissionEvents,
  listProjectMissions,
  listProjects,
  startMission,
  stopMission,
  streamMissionEvents,
} from "../../api/workMode";
import { normalizeAgents } from "../../domain/agents";
import ActivityStrip from "./components/ActivityStrip";
import InspectorPanel from "./components/InspectorPanel";
import MissionHeader from "./components/MissionHeader";
import ProductPanel from "./components/ProductPanel";
import ProgressTimeline from "./components/ProgressTimeline";
import ProjectMissionRail from "./components/ProjectMissionRail";
import RawLogPanel from "./components/RawLogPanel";
import ReliabilityPanel from "./components/ReliabilityPanel";
import WarningCard from "./components/WarningCard";
import WorkWindowPanel from "./components/WorkWindowPanel";
import WorkspaceView from "./components/WorkspaceView";

const terminalStatuses = new Set(["completed", "failed", "stopped", "blocked"]);

function WorkPage({ agents = [] }) {
  const workAgents = useMemo(() => normalizeAgents(agents).slice(0, 2), [agents]);
  const defaultLeadId = workAgents[0]?.slot || "agent_1";
  const [projects, setProjects] = useState([]);
  const [missions, setMissions] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);
  const [selectedMission, setSelectedMission] = useState(null);
  const [events, setEvents] = useState([]);
  const [artifacts, setArtifacts] = useState([]);
  const [products, setProducts] = useState([]);
  const [workWindows, setWorkWindows] = useState([]);
  const [projectName, setProjectName] = useState("");
  const [missionLeadId, setMissionLeadId] = useState(defaultLeadId);
  const [missionTitle, setMissionTitle] = useState("");
  const [missionGoal, setMissionGoal] = useState("");
  const [showMissionCreate, setShowMissionCreate] = useState(false);
  const [answerText, setAnswerText] = useState("");
  const [followUpText, setFollowUpText] = useState("");
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const afterSequence = useMemo(() => Math.max(0, ...events.map((event) => event.sequence || 0)), [events]);
  const afterSequenceRef = useRef(0);
  const inputRequest = useMemo(
    () => [...events].reverse().find((event) => event.type === "USER_INPUT_REQUESTED") || null,
    [events],
  );

  useEffect(() => {
    afterSequenceRef.current = afterSequence;
  }, [afterSequence]);

  useEffect(() => {
    let mounted = true;

    async function load() {
      setLoading(true);
      setError("");
      try {
        const rows = await listProjects();
        if (!mounted) return;
        setProjects(rows);
        setSelectedProject(null);
        setMissionLeadId(defaultLeadId);
        setMissions([]);
        setSelectedMission(null);
        setEvents([]);
        setArtifacts([]);
        setProducts([]);
        setWorkWindows([]);
        setAnswerText("");
        setFollowUpText("");
      } catch (err) {
        if (mounted) setError(err.message || "Load failed");
      } finally {
        if (mounted) setLoading(false);
      }
    }

    load();
    return () => {
      mounted = false;
    };
  }, []);

  useEffect(() => {
    if (!workAgents.some((agent) => agent.slot === missionLeadId)) {
      setMissionLeadId(defaultLeadId);
    }
  }, [defaultLeadId, missionLeadId, workAgents]);

  useEffect(() => {
    if (!selectedMission || terminalStatuses.has(selectedMission.status)) return undefined;
    if (!["running", "stopping"].includes(selectedMission.status)) return undefined;
    let stopped = false;
    let pollingTimer = null;
    const controller = new AbortController();

    async function refreshWithEvents(nextEvents) {
      if (stopped || nextEvents.length === 0) return;
      const detail = await getMission(selectedMission.id);
      if (stopped) return;
      setSelectedMission(detail.mission);
      setMissions((current) => replaceMission(current, detail.mission));
      setEvents((current) => mergeEvents(current, nextEvents));
      setArtifacts(detail.artifacts || []);
      setProducts(detail.products || []);
      setWorkWindows(detail.workWindows || []);
    }

    function startPollingFallback() {
      if (pollingTimer !== null) return;
      pollingTimer = window.setInterval(async () => {
        try {
          const nextEvents = await listMissionEvents(selectedMission.id, afterSequenceRef.current);
          await refreshWithEvents(nextEvents);
        } catch (err) {
          if (!stopped) setError(err.message || "Poll failed");
        }
      }, 1500);
    }

    async function startStream() {
      try {
        await streamMissionEvents(selectedMission.id, afterSequenceRef.current, {
          signal: controller.signal,
          onEvent: async (event) => {
            await refreshWithEvents([event]);
          },
        });
        if (!stopped) {
          const detail = await getMission(selectedMission.id);
          if (stopped) return;
          setSelectedMission(detail.mission);
          setMissions((current) => replaceMission(current, detail.mission));
          setEvents(detail.events || []);
          setArtifacts(detail.artifacts || []);
          setProducts(detail.products || []);
          setWorkWindows(detail.workWindows || []);
          if (["running", "stopping"].includes(detail.mission?.status)) {
            startPollingFallback();
          }
        }
      } catch (err) {
        if (!stopped && err.name !== "AbortError") {
          startPollingFallback();
        }
      }
    }

    startStream();
    return () => {
      stopped = true;
      controller.abort();
      if (pollingTimer !== null) window.clearInterval(pollingTimer);
    };
  }, [selectedMission?.id, selectedMission?.status]);

  async function addProject() {
    if (!projectName.trim() || busy) return;
    setBusy(true);
    setError("");
    try {
      const project = await createProject({ name: projectName });
      setProjects((current) => [project, ...current]);
      setProjectName("");
      await loadProject(project);
    } catch (err) {
      setError(err.message || "Create failed");
    } finally {
      setBusy(false);
    }
  }

  async function selectProject(project) {
    if (busy || project.id === selectedProject?.id) return;
    setBusy(true);
    setError("");
    try {
      await loadProject(project);
    } catch (err) {
      setError(err.message || "Load failed");
    } finally {
      setBusy(false);
    }
  }

  async function loadProject(project) {
    const missionRows = await listProjectMissions(project.id);
    const firstMission = missionRows[0] || null;
    const detail = firstMission ? await getMission(firstMission.id) : null;
    const selected = detail?.mission || firstMission;
    setSelectedProject(project);
    setMissionLeadId(defaultLeadId);
    setMissions(replaceMission(missionRows, selected));
    setSelectedMission(selected);
    setEvents(detail?.events || []);
    setArtifacts(detail?.artifacts || []);
    setProducts(detail?.products || []);
    setWorkWindows(detail?.workWindows || []);
    setAnswerText("");
    setFollowUpText("");
  }

  function backToWorkspace() {
    if (busy) return;
    setError("");
    setSelectedProject(null);
    setMissions([]);
    setSelectedMission(null);
    setEvents([]);
    setArtifacts([]);
    setProducts([]);
    setWorkWindows([]);
    setMissionLeadId(defaultLeadId);
    setMissionTitle("");
    setMissionGoal("");
    setShowMissionCreate(false);
    setAnswerText("");
    setFollowUpText("");
  }

  async function addMission() {
    if (!selectedProject || !missionTitle.trim() || !missionGoal.trim() || busy) return;
    setBusy(true);
    setError("");
    try {
      const leadId = workAgents.some((agent) => agent.slot === missionLeadId) ? missionLeadId : defaultLeadId;
      const mission = await createMission({
        projectId: selectedProject.id,
        title: missionTitle,
        goal: missionGoal,
        leadEmployeeId: leadId,
      });
      const detail = await getMission(mission.id);
      setMissions((current) => [detail.mission, ...current]);
      setSelectedMission(detail.mission);
      setEvents(detail.events || []);
      setArtifacts(detail.artifacts || []);
      setProducts(detail.products || []);
      setWorkWindows(detail.workWindows || []);
      if (detail.mission?.status !== "waiting_input") setAnswerText("");
      setAnswerText("");
      setFollowUpText("");
      setMissionTitle("");
      setMissionGoal("");
      setShowMissionCreate(false);
    } catch (err) {
      setError(err.message || "Create failed");
    } finally {
      setBusy(false);
    }
  }

  async function selectMission(mission) {
    if (busy || mission.id === selectedMission?.id) return;
    setBusy(true);
    setError("");
    try {
      const detail = await getMission(mission.id);
      setSelectedMission(detail.mission);
      setMissions((current) => replaceMission(current, detail.mission));
      setEvents(detail.events || []);
      setArtifacts(detail.artifacts || []);
      setProducts(detail.products || []);
      setWorkWindows(detail.workWindows || []);
      if (detail.mission?.status !== "waiting_input") setAnswerText("");
      setAnswerText("");
      setFollowUpText("");
    } catch (err) {
      setError(err.message || "Load failed");
    } finally {
      setBusy(false);
    }
  }

  async function start() {
    if (!selectedMission || busy) return;
    setBusy(true);
    setError("");
    try {
      const detail = await startMission(selectedMission.id);
      setSelectedMission(detail.mission);
      setMissions((current) => replaceMission(current, detail.mission));
      setEvents(detail.events || []);
      setArtifacts(detail.artifacts || []);
      setProducts(detail.products || []);
      setWorkWindows(detail.workWindows || []);
      setFollowUpText("");
    } catch (err) {
      setError(err.message || "Start failed");
    } finally {
      setBusy(false);
    }
  }

  async function stop() {
    if (!selectedMission || busy) return;
    setBusy(true);
    setError("");
    try {
      const detail = await stopMission(selectedMission.id, { reason: "Stopped by user" });
      setSelectedMission(detail.mission);
      setMissions((current) => replaceMission(current, detail.mission));
      setEvents(detail.events || []);
      setArtifacts(detail.artifacts || []);
      setProducts(detail.products || []);
      setWorkWindows(detail.workWindows || []);
    } catch (err) {
      setError(err.message || "Stop failed");
    } finally {
      setBusy(false);
    }
  }

  async function answer(event) {
    event.preventDefault();
    if (!selectedMission || busy || !answerText.trim()) return;
    setBusy(true);
    setError("");
    try {
      const detail = await answerMission(selectedMission.id, { answer: answerText });
      setSelectedMission(detail.mission);
      setMissions((current) => replaceMission(current, detail.mission));
      setEvents(detail.events || []);
      setArtifacts(detail.artifacts || []);
      setProducts(detail.products || []);
      setWorkWindows(detail.workWindows || []);
      setAnswerText("");
    } catch (err) {
      setError(err.message || "Reply failed");
    } finally {
      setBusy(false);
    }
  }

  async function continueFollowUp(event) {
    event.preventDefault();
    if (!selectedMission || busy || !followUpText.trim()) return;
    setBusy(true);
    setError("");
    try {
      const detail = await continueMissionFollowUp(selectedMission.id, { request: followUpText });
      setSelectedMission(detail.mission);
      setMissions((current) => replaceMission(current, detail.mission));
      setEvents(detail.events || []);
      setArtifacts(detail.artifacts || []);
      setProducts(detail.products || []);
      setWorkWindows(detail.workWindows || []);
      setFollowUpText("");
    } catch (err) {
      setError(err.message || "Continue failed");
    } finally {
      setBusy(false);
    }
  }

  async function evaluate() {
    if (!selectedMission || busy) return;
    setBusy(true);
    setError("");
    try {
      const detail = await evaluateMission(selectedMission.id);
      setSelectedMission(detail.mission);
      setMissions((current) => replaceMission(current, detail.mission));
      setEvents(detail.events || []);
      setArtifacts(detail.artifacts || []);
      setProducts(detail.products || []);
      setWorkWindows(detail.workWindows || []);
    } catch (err) {
      setError(err.message || "Evaluate failed");
    } finally {
      setBusy(false);
    }
  }

  if (!selectedProject) {
    return (
      <WorkspaceView
        busy={busy || loading}
        error={error}
        loading={loading}
        onCreateProject={addProject}
        onProjectNameChange={setProjectName}
        onSelectProject={selectProject}
        projectName={projectName}
        projects={projects}
      />
    );
  }

  return (
    <div className="work-console-grid">
      <ProjectMissionRail
        agents={workAgents}
        busy={busy || loading}
        missionLeadId={missionLeadId}
        missionGoal={missionGoal}
        missionTitle={missionTitle}
        missions={missions}
        onBackToWorkspace={backToWorkspace}
        onCreateMission={addMission}
        onMissionLeadChange={setMissionLeadId}
        onMissionGoalChange={setMissionGoal}
        onMissionTitleChange={setMissionTitle}
        onSelectMission={selectMission}
        onShowCreateMission={() => setShowMissionCreate((current) => !current)}
        selectedMission={selectedMission}
        selectedProject={selectedProject}
        showMissionCreate={showMissionCreate}
      />
      <section className="mission-console">
        <MissionHeader
          answerText={answerText}
          busy={busy || loading}
          followUpText={followUpText}
          inputRequest={inputRequest}
          mission={selectedMission}
          onAnswer={answer}
          onAnswerTextChange={setAnswerText}
          onEvaluate={evaluate}
          onFollowUp={continueFollowUp}
          onFollowUpTextChange={setFollowUpText}
          onStart={start}
          onStop={stop}
        />
        <div className="mission-content">
          <ActivityStrip events={events} mission={selectedMission} />
          <ReliabilityPanel artifacts={artifacts} events={events} />
          <WorkWindowPanel artifacts={artifacts} workWindows={workWindows} />
          <ProductPanel artifacts={artifacts} products={products} />
          <ProgressTimeline events={events} />
          <RawLogPanel events={events} />
        </div>
      </section>
      <div className="work-side">
        <InspectorPanel
          busy={busy || loading}
          error={error}
          agentCount={workAgents.length}
          mission={selectedMission}
          project={selectedProject}
        />
        <WarningCard events={events} />
      </div>
    </div>
  );
}

function mergeEvents(current, nextEvents) {
  const map = new Map(current.map((event) => [event.id, event]));
  for (const event of nextEvents) {
    map.set(event.id, event);
  }
  return Array.from(map.values()).sort((a, b) => a.sequence - b.sequence);
}

function replaceMission(missions, mission) {
  if (!mission) return missions;
  return missions.map((item) => (item.id === mission.id ? mission : item));
}

export default WorkPage;
