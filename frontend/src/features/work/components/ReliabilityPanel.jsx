/*
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
*/
function ReliabilityPanel({ artifacts = [] }) {
  const report = latestReport(artifacts);
  if (!report) return null;
  const issues = report.issues || [];
  const topIssues = issues.slice(0, 4);
  const requirements = (report.requirements || []).slice(0, 5);
  const claims = (report.claims || []).slice(0, 5);
  const evidence = report.evidence || [];
  const toolFailures = (report.toolFailures || []).slice(0, 5);
  const suggestedActions = (report.suggestedNextActions || []).slice(0, 4);
  const limitations = (report.limitations || []).slice(0, 3);

  return (
    <div className={`work-card reliability-panel status-${report.status}`}>
      <div className="card-head reliability-head">
        <div>
          <p className="eyebrow">Reliability</p>
          <h2>{report.score} / 100</h2>
        </div>
        <span>{statusLabel(report.status)}</span>
      </div>
      <p className="reliability-summary">{report.summary}</p>
      <div className="reliability-badges">
        {issueBadges(report.issueCounts).map(([label, count]) => (
          <span key={label}>
            {count} {label}
          </span>
        ))}
        <span>{evidence.length} evidence</span>
        {report.mode && <span>{report.mode}</span>}
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
    </div>
  );
}

function latestReport(artifacts) {
  const reports = artifacts
    .filter((artifact) => artifact.metadata?.artifactRole === "reliability_report")
    .sort((left, right) => new Date(right.createdAt || 0).getTime() - new Date(left.createdAt || 0).getTime());
  return reports[0]?.metadata?.reportPayload || null;
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
