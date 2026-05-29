/*
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-29
Last Modified by: Codex
*/
import { ChevronRight, ShieldCheck } from "lucide-react";
import { useState } from "react";
import { formatEventTime } from "./eventDisplay";
import { formatEasternTime } from "./timeFormat";

function ReliabilityPanel({ artifacts = [], compact = false, events = [] }) {
  const { report, history } = reliabilityReports(artifacts, events);
  if (!report) return null;
  if (compact) return <CompactReliabilityPanel history={history} report={report} />;
  return <ReliabilityReportBody history={history} report={report} shellClass="work-card reliability-panel" />;
}

export function reliabilitySummary(artifacts = [], events = []) {
  const { report } = reliabilityReports(artifacts, events);
  if (!report) return null;
  const issues = report.issues || [];
  const evidence = report.evidence || [];
  const issueCount = issues.length || Object.values(report.issueCounts || {}).reduce((sum, count) => sum + Number(count || 0), 0);
  return {
    evidenceCount: evidence.length,
    issueCount,
    score: report.score,
    status: statusLabel(report.status),
  };
}

function CompactReliabilityPanel({ history, report }) {
  const issues = report.issues || [];
  const evidence = report.evidence || [];
  const issueCount = issues.length || Object.values(report.issueCounts || {}).reduce((sum, count) => sum + Number(count || 0), 0);
  return (
    <section className={`quality-panel status-${report.status}`} aria-label="Quality">
      <div className="quality-head">
        <div>
          <p className="eyebrow">Quality</p>
          <h2>
            Risk <span>{report.score} / 100</span>
          </h2>
        </div>
        <ShieldCheck size={20} />
      </div>
      <div className="quality-grid">
        <span>{statusLabel(report.status)}</span>
        <span>{confidenceShortLabel(report.confidence)}</span>
        <span>{issueCount} issues</span>
        <span>{evidence.length} evidence</span>
      </div>
      <p>{report.summary || report.scoreMeaning || "Trace-backed risk score, not proof."}</p>
      <details className="quality-details">
        <summary>
          <ChevronRight size={14} />
          <span>Review details</span>
        </summary>
        <ReliabilityReportBody history={history} report={report} shellClass="reliability-panel embedded" />
      </details>
    </section>
  );
}

function ReliabilityReportBody({ history = [], report, shellClass }) {
  const reports = useSelectableReports(report, history);
  const activeReport = reports.activeReport;
  const issues = activeReport.issues || [];
  const topIssues = issues.slice(0, 4);
  const requirements = (activeReport.requirements || []).slice(0, 5);
  const claims = (activeReport.claims || []).slice(0, 5);
  const evidence = activeReport.evidence || [];
  const toolFailures = (activeReport.toolFailures || []).slice(0, 5);
  const suggestedActions = (activeReport.suggestedNextActions || []).slice(0, 4);
  const limitations = (activeReport.limitations || []).slice(0, 3);

  return (
    <div className={`${shellClass} status-${activeReport.status}`}>
      <div className="card-head reliability-head">
        <div>
          <p className="eyebrow">Reliability</p>
          <h2>{activeReport.score} / 100</h2>
        </div>
        <span>{statusLabel(activeReport.status)}</span>
      </div>
      <p className="reliability-meta">
        {reportTimeLabel(activeReport)}
      </p>
      <div className="reliability-confidence">
        <span>Risk score</span>
        <strong>{activeReport.scoreMeaning || "Trace-backed risk score, not proof."}</strong>
        <small>{confidenceLabel(activeReport.confidence, activeReport.confidenceReason)}</small>
      </div>
      <p className="reliability-summary">{activeReport.summary}</p>
      <div className="reliability-badges">
        {issueBadges(activeReport.issueCounts).map(([label, count]) => (
          <span key={label}>
            {count} {label}
          </span>
        ))}
        <span>{evidence.length} evidence</span>
        {activeReport.mode && <span>{activeReport.mode}</span>}
        {issues.length === 0 && <span>Clear</span>}
      </div>
      <div className="reliability-evidence">
        <span>Evidence ledger</span>
        <strong>{evidence.length ? `${evidence.length} sources` : "No trace evidence"}</strong>
      </div>
      {toolFailures.length > 0 && (
        <div className="reliability-section">
          <strong>Tool failures</strong>
          <div className="reliability-table">
            {toolFailures.map((failure) => (
              <div key={failure.id || failure.eventId}>
                <span>#{failure.eventSequence}</span>
                <p className="reliability-rich">
                  <strong>{failure.tool || "tool"}</strong>
                  <small>{failure.code || failure.message || "failed"}</small>
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
      {topIssues.length > 0 && (
        <div className="reliability-section">
          <strong>Issues</strong>
          {topIssues.map((issue) => (
            <div className={`reliability-issue severity-${issue.severity}`} key={issue.id}>
              <span>{issue.severity}</span>
              <p>{issue.title}</p>
              {issue.description && <small>{issue.description}</small>}
              {issue.type && <small>{issueTypeLabel(issue.type)}</small>}
              <small>{issue.suggestedFix}</small>
            </div>
          ))}
        </div>
      )}
      {suggestedActions.length > 0 && (
        <div className="reliability-section">
          <strong>Suggested fixes</strong>
          <div className="reliability-list">
            {suggestedActions.map((action) => (
              <p key={action}>{action}</p>
            ))}
          </div>
        </div>
      )}
      {requirements.length > 0 && (
        <div className="reliability-section">
          <strong>Requirements</strong>
          <div className="reliability-table">
            {requirements.map((item) => (
              <div key={item.id}>
                <span>{item.status}</span>
                <p className="reliability-rich">
                  <strong>{item.requirement}</strong>
                  {item.evidence && <small>{item.evidence}</small>}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
      {claims.length > 0 && (
        <div className="reliability-section">
          <strong>Claims</strong>
          <div className="reliability-table">
            {claims.map((claim) => (
              <div key={claim.id}>
                <span>{supportLabel(claim.supportLevel)}</span>
                <p className="reliability-rich">
                  <strong>{claim.text}</strong>
                  {claim.reason && <small>{claim.reason}</small>}
                  {claim.bestEvidenceIds?.length > 0 && <small>{bestSourceLabel(claim.bestEvidenceIds, evidence)}</small>}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
      {evidence.length > 0 && (
        <div className="reliability-section">
          <strong>Evidence</strong>
          <div className="reliability-table">
            {evidence.slice(0, 4).map((item) => (
              <div key={item.id}>
                <span>{item.id}</span>
                <p>
                  <a href={item.url} rel="noreferrer" target="_blank">
                    {item.title || item.source || item.url}
                  </a>
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
      {limitations.length > 0 && (
        <div className="reliability-section">
          <strong>Limitations</strong>
          <div className="reliability-list muted-list">
            {limitations.map((item) => (
              <p key={item}>{item}</p>
            ))}
          </div>
        </div>
      )}
      {reports.allReports.length > 1 && (
        <details className="reliability-history">
          <summary>
            <ChevronRight size={14} />
            <span>History</span>
            <small>{reports.allReports.length}</small>
          </summary>
          <div className="reliability-history-list">
            {reports.allReports.map((item) => (
              <button
                className={reports.activeKey === reportKey(item) ? "reliability-history-row active" : "reliability-history-row"}
                key={reportKey(item)}
                onClick={() => reports.setActiveKey(reportKey(item))}
                type="button"
              >
                <span>{item.score} / 100</span>
                <p>
                  <strong>{statusLabel(item.status)}</strong>
                  <small>
                    {reportTimeLabel(item)}
                    {item.mode ? ` / ${item.mode}` : ""}
                  </small>
                </p>
              </button>
            ))}
          </div>
        </details>
      )}
    </div>
  );
}

function useSelectableReports(report, history) {
  const allReports = [report, ...history].filter(Boolean);
  const [activeKey, setActiveKey] = useState(reportKey(report));
  const activeReport = allReports.find((item) => reportKey(item) === activeKey) || report;
  return { activeKey, activeReport, allReports, setActiveKey };
}

function confidenceShortLabel(confidence) {
  return (
    {
      high: "High conf.",
      low: "Low conf.",
      medium: "Med. conf.",
    }[confidence] || "No conf."
  );
}

function reliabilityReports(artifacts, events) {
  const artifactReports = artifacts
    .filter((artifact) => artifact.metadata?.artifactRole === "reliability_report")
    .map((artifact) => reportFromArtifact(artifact))
    .filter(Boolean);
  const reportsByArtifactId = new Map(artifactReports.map((item) => [item.reportArtifactId, item]));
  const reportEvents = events
    .filter((event) => event.type === "RELIABILITY_REPORTED")
    .sort((left, right) => (right.sequence || 0) - (left.sequence || 0));
  const eventBackedReports = reportEvents
    .map((event) => reportFromEvent(event, reportsByArtifactId))
    .filter(Boolean);
  const ordered = uniqueReports([...eventBackedReports, ...artifactReports]);
  return {
    report: ordered[0] || null,
    history: ordered.slice(1),
  };
}

function reportFromArtifact(artifact) {
  const report = artifact.metadata?.reportPayload;
  if (!report) return null;
  return {
    ...report,
    reportArtifactId: report.reportArtifactId || artifact.id,
    createdAt: report.createdAt || artifact.createdAt,
    artifactCreatedAt: artifact.createdAt,
  };
}

function reportFromEvent(event, reportsByArtifactId) {
  const artifactId = event.payload?.reportArtifactId || "";
  const report = reportsByArtifactId.get(artifactId);
  if (!report && event.payload?.score == null) return null;
  return {
    ...(report || {}),
    reportArtifactId: artifactId || report?.reportArtifactId,
    reportId: report?.reportId || artifactId || event.id,
    score: report?.score ?? event.payload?.score,
    status: report?.status || event.payload?.status,
    issueCounts: report?.issueCounts || event.payload?.issueCounts || {},
    mode: report?.mode || event.payload?.mode,
    objective: report?.objective ?? event.payload?.objective ?? false,
    profile: report?.profile || event.payload?.profile,
    scoreMeaning:
      report?.scoreMeaning ||
      event.payload?.scoreMeaning ||
      "Trace-backed reliability risk score, not proof of correctness.",
    confidence: report?.confidence || event.payload?.confidence || "low",
    confidenceReason: report?.confidenceReason || event.payload?.confidenceReason || "",
    eventSequence: event.sequence,
    eventCreatedAt: event.createdAt,
    eventTime: formatEventTime(event),
    summary: report?.summary || event.message || "",
    issues: report?.issues || [],
    requirements: report?.requirements || [],
    claims: report?.claims || [],
    evidence: report?.evidence || [],
    toolFailures: report?.toolFailures || [],
    suggestedNextActions: report?.suggestedNextActions || [],
    limitations: report?.limitations || [],
  };
}

function reportKey(report) {
  return report?.reportArtifactId || report?.reportId || String(report?.eventSequence || "latest");
}

function reportTimeLabel(report) {
  const raw = report.eventCreatedAt || report.createdAt || report.artifactCreatedAt;
  return formatEasternTime(raw) || report.eventTime || "Latest report";
}

function uniqueReports(reports) {
  const seen = new Set();
  const unique = [];
  for (const report of reports) {
    const key = report.reportArtifactId || report.reportId;
    if (!key || seen.has(key)) continue;
    seen.add(key);
    unique.push(report);
  }
  return unique.sort((left, right) => {
    if ((right.eventSequence || 0) !== (left.eventSequence || 0)) {
      return (right.eventSequence || 0) - (left.eventSequence || 0);
    }
    return new Date(right.artifactCreatedAt || 0).getTime() - new Date(left.artifactCreatedAt || 0).getTime();
  });
}

function confidenceLabel(confidence, reason) {
  const label =
    {
      high: "High confidence",
      low: "Low confidence",
      medium: "Medium confidence",
    }[confidence] || "Confidence not set";
  return reason ? `${label}: ${reason}` : label;
}

function statusLabel(status) {
  return {
    minor_review: "Minor review",
    needs_human_review: "Needs review",
    ship_ready: "Ship-ready",
    unsafe_to_ship: "Unsafe",
  }[status] || "Review";
}

function issueBadges(issueCounts = {}) {
  const severityOrder = ["critical", "high", "medium", "low"];
  const severity = severityOrder
    .filter((key) => issueCounts[key])
    .map((key) => [key, issueCounts[key]]);
  const types = Object.entries(issueCounts)
    .filter(([key, count]) => key.startsWith("type:") && count)
    .slice(0, 4)
    .map(([key, count]) => [issueTypeLabel(key.slice(5)), count]);
  return [...severity, ...types];
}

function issueTypeLabel(type) {
  return {
    evaluation_limitation: "limitation",
    hallucinated_entity: "entity risk",
    missing_requirement: "missing req",
    missing_source: "missing source",
    mission_incomplete: "incomplete",
    tool_failure_ignored: "tool failure",
    unsupported_claim: "unsupported",
    unsafe_action: "unsafe",
    weakly_supported_claim: "weak support",
  }[type] || type;
}

function supportLabel(level) {
  return {
    contradicted: "Contradicted",
    none: "Unsupported",
    not_evaluable: "No evidence",
    strong: "Supported",
    weak: "Weak",
  }[level] || level;
}

function bestSourceLabel(ids = [], evidence = []) {
  const source = evidence.find((item) => ids.includes(item.id));
  if (!source) return `Source ${ids.join(", ")}`;
  const host = source.source || safeHost(source.url);
  return `Best source: ${host || source.title || source.id}`;
}

function safeHost(url) {
  try {
    return new URL(url).hostname;
  } catch {
    return "";
  }
}

export default ReliabilityPanel;
