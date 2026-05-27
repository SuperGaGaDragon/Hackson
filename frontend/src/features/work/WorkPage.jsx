/*
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-27
Last Modified by: Codex
*/
import { useEffect, useMemo, useState } from "react";
import {
  addProjectEmployee,
  createEmployee,
  createMission,
  createProject,
  getMission,
  listEmployees,
  listMissionEvents,
  listProjectEmployees,
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
import WorkspaceView from "./components/WorkspaceView";

const terminalStatuses = new Set(["completed", "failed", "stopped", "blocked"]);

function WorkPage() {
  const [projects, setProjects] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [team, setTeam] = useState([]);
  const [missions, setMissions] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);
  const [selectedMission, setSelectedMission] = useState(null);
  const [events, setEvents] = useState([]);
  const [projectName, setProjectName] = useState("");
  const [employeeName, setEmployeeName] = useState("");
  const [employeeRole, setEmployeeRole] = useState("");
  const [teamEmployeeId, setTeamEmployeeId] = useState("");
  const [missionLeadId, setMissionLeadId] = useState("employee_default_lead");
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
        const employeeRows = await listEmployees();
        if (!mounted) return;
        setProjects(rows);
        setEmployees(employeeRows);
        setSelectedProject(null);
        setTeam([]);
        setTeamEmployeeId(firstAvailableEmployeeId(employeeRows, []));
        setMissionLeadId("employee_default_lead");
        setMissions([]);
        setSelectedMission(null);
        setEvents([]);
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

  async function loadProject(project, employeeRows = employees) {
    const missionRows = await listProjectMissions(project.id);
    const teamRows = await listProjectEmployees(project.id);
    const firstMission = missionRows[0] || null;
    const detail = firstMission ? await getMission(firstMission.id) : null;
    const selected = detail?.mission || firstMission;
    setSelectedProject(project);
    setTeam(teamRows);
    setTeamEmployeeId(firstAvailableEmployeeId(employeeRows, teamRows));
    setMissionLeadId(firstLeadId(teamRows));
    setMissions(replaceMission(missionRows, selected));
    setSelectedMission(selected);
    setEvents(detail?.events || []);
  }

  function backToWorkspace() {
    if (busy) return;
    setError("");
    setSelectedProject(null);
    setTeam([]);
    setMissions([]);
    setSelectedMission(null);
    setEvents([]);
    setTeamEmployeeId(firstAvailableEmployeeId(employees, []));
    setMissionLeadId("employee_default_lead");
    setEmployeeName("");
    setEmployeeRole("");
    setMissionTitle("");
    setMissionGoal("");
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
        leadEmployeeId: missionLeadId,
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

  async function addEmployee() {
    if (!employeeName.trim() || !employeeRole.trim() || busy) return;
    setBusy(true);
    setError("");
    try {
      const employee = await createEmployee({ name: employeeName, role: employeeRole });
      const nextEmployees = [employee, ...employees];
      setEmployees(nextEmployees);
      setTeamEmployeeId(firstAvailableEmployeeId(nextEmployees, team));
      setEmployeeName("");
      setEmployeeRole("");
    } catch (err) {
      setError(err.message || "Create failed");
    } finally {
      setBusy(false);
    }
  }

  async function addToTeam() {
    if (!selectedProject || !teamEmployeeId || busy) return;
    setBusy(true);
    setError("");
    try {
      const member = await addProjectEmployee(selectedProject.id, {
        employeeId: teamEmployeeId,
        roleOnProject: "Member",
      });
      const nextTeam = mergeTeam(team, [member]);
      setTeam(nextTeam);
      setTeamEmployeeId(firstAvailableEmployeeId(employees, nextTeam));
      setMissionLeadId(member.employeeId);
    } catch (err) {
      setError(err.message || "Add failed");
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
        busy={busy || loading}
        employeeName={employeeName}
        employeeRole={employeeRole}
        employees={employees}
        missionLeadId={missionLeadId}
        missionGoal={missionGoal}
        missionTitle={missionTitle}
        missions={missions}
        onAddEmployee={addEmployee}
        onAddToTeam={addToTeam}
        onBackToWorkspace={backToWorkspace}
        onCreateMission={addMission}
        onEmployeeNameChange={setEmployeeName}
        onEmployeeRoleChange={setEmployeeRole}
        onMissionLeadChange={setMissionLeadId}
        onMissionGoalChange={setMissionGoal}
        onMissionTitleChange={setMissionTitle}
        onSelectMission={selectMission}
        onTeamEmployeeChange={setTeamEmployeeId}
        selectedMission={selectedMission}
        selectedProject={selectedProject}
        team={team}
        teamEmployeeId={teamEmployeeId}
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
        <InspectorPanel
          busy={busy || loading}
          error={error}
          mission={selectedMission}
          project={selectedProject}
          teamCount={team.length}
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

function mergeTeam(current, nextRows) {
  const map = new Map(current.map((item) => [item.id, item]));
  for (const row of nextRows) {
    map.set(row.id, row);
  }
  return Array.from(map.values());
}

function firstLeadId(team) {
  return team[0]?.employeeId || "employee_default_lead";
}

function firstAvailableEmployeeId(employees, team) {
  const used = new Set(team.map((member) => member.employeeId));
  return employees.find((employee) => !used.has(employee.id))?.id || "";
}

export default WorkPage;
