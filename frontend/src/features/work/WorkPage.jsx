/*
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-27
Last Modified by: Codex
*/
import { useEffect, useMemo, useState } from "react";
import {
  createMission,
  createProject,
  getMission,
  listMissionEvents,
  listProjectMissions,
  listProjects,
  startMission,
  stopMission,
} from "../../api/workMode";
import InspectorPanel from "./components/InspectorPanel";
import MissionHeader from "./components/MissionHeader";
import ProductPanel from "./components/ProductPanel";
import ProgressTimeline from "./components/ProgressTimeline";
import ProjectMissionRail from "./components/ProjectMissionRail";
import RawLogPanel from "./components/RawLogPanel";
import SummaryCard from "./components/SummaryCard";
import WarningCard from "./components/WarningCard";

const terminalStatuses = new Set(["completed", "failed", "stopped", "blocked"]);

function WorkPage() {
  const [projects, setProjects] = useState([]);
  const [missions, setMissions] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);
  const [selectedMission, setSelectedMission] = useState(null);
  const [events, setEvents] = useState([]);
  const [projectName, setProjectName] = useState("");
  const [projectRepoPath, setProjectRepoPath] = useState("");
  const [missionTitle, setMissionTitle] = useState("");
  const [missionGoal, setMissionGoal] = useState("");
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const afterSequence = useMemo(() => Math.max(0, ...events.map((event) => event.sequence || 0)), [events]);

  useEffect(() => {
    let mounted = true;

    async function load() {
      setLoading(true);
      setError("");
      try {
        const rows = await listProjects();
        const firstProject = rows[0] || null;
        const missionRows = firstProject ? await listProjectMissions(firstProject.id) : [];
        const firstMission = missionRows[0] || null;
        const detail = firstMission ? await getMission(firstMission.id) : null;
        if (!mounted) return;
        setProjects(rows);
        setSelectedProject(firstProject);
        const selected = detail?.mission || firstMission;
        setMissions(replaceMission(missionRows, selected));
        setSelectedMission(selected);
        setEvents(detail?.events || []);
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
    if (!selectedMission || terminalStatuses.has(selectedMission.status)) return undefined;
    if (!["running", "stopping"].includes(selectedMission.status)) return undefined;
    const timer = window.setInterval(async () => {
      try {
        const nextEvents = await listMissionEvents(selectedMission.id, afterSequence);
        if (nextEvents.length > 0) {
          setEvents((current) => mergeEvents(current, nextEvents));
          const detail = await getMission(selectedMission.id);
          setSelectedMission(detail.mission);
          setMissions((current) => replaceMission(current, detail.mission));
        }
      } catch (err) {
        setError(err.message || "Poll failed");
      }
    }, 1500);
    return () => window.clearInterval(timer);
  }, [afterSequence, selectedMission]);

  async function addProject() {
    if (!projectName.trim() || !projectRepoPath.trim() || busy) return;
    setBusy(true);
    setError("");
    try {
      const project = await createProject({ name: projectName, repoPath: projectRepoPath });
      setProjects((current) => [project, ...current]);
      setSelectedProject(project);
      setMissions([]);
      setSelectedMission(null);
      setEvents([]);
      setProjectName("");
      setProjectRepoPath("");
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
      const missionRows = await listProjectMissions(project.id);
      const firstMission = missionRows[0] || null;
      const detail = firstMission ? await getMission(firstMission.id) : null;
      const selected = detail?.mission || firstMission;
      setSelectedProject(project);
      setMissions(replaceMission(missionRows, selected));
      setSelectedMission(selected);
      setEvents(detail?.events || []);
    } catch (err) {
      setError(err.message || "Load failed");
    } finally {
      setBusy(false);
    }
  }

  async function addMission() {
    if (!selectedProject || !missionTitle.trim() || !missionGoal.trim() || busy) return;
    setBusy(true);
    setError("");
    try {
      const mission = await createMission({
        projectId: selectedProject.id,
        title: missionTitle,
        goal: missionGoal,
      });
      const detail = await getMission(mission.id);
      setMissions((current) => [detail.mission, ...current]);
      setSelectedMission(detail.mission);
      setEvents(detail.events || []);
      setMissionTitle("");
      setMissionGoal("");
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
    } catch (err) {
      setError(err.message || "Stop failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="work-console-grid">
      <ProjectMissionRail
        busy={busy || loading}
        missionGoal={missionGoal}
        missionTitle={missionTitle}
        missions={missions}
        onCreateMission={addMission}
        onCreateProject={addProject}
        onMissionGoalChange={setMissionGoal}
        onMissionTitleChange={setMissionTitle}
        onProjectNameChange={setProjectName}
        onProjectRepoPathChange={setProjectRepoPath}
        onSelectMission={selectMission}
        onSelectProject={selectProject}
        projectName={projectName}
        projectRepoPath={projectRepoPath}
        projects={projects}
        selectedMission={selectedMission}
        selectedProject={selectedProject}
      />
      <section className="mission-console">
        <MissionHeader busy={busy || loading} mission={selectedMission} onStart={start} onStop={stop} />
        <div className="mission-content">
          <ProgressTimeline events={events} />
          <SummaryCard events={events} />
          <ProductPanel events={events} />
          <RawLogPanel events={events} />
        </div>
      </section>
      <div className="work-side">
        <InspectorPanel busy={busy || loading} error={error} mission={selectedMission} project={selectedProject} />
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
