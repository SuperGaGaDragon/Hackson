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
        {Object.entries(report.issueCounts || {}).map(([severity, count]) => (
          <span key={severity}>
            {count} {severity}
          </span>
        ))}
        {issues.length === 0 && <span>Clear</span>}
      </div>
      {topIssues.length > 0 && (
        <div className="reliability-section">
          <strong>Issues</strong>
          {topIssues.map((issue) => (
            <div className={`reliability-issue severity-${issue.severity}`} key={issue.id}>
              <span>{issue.severity}</span>
              <p>{issue.title}</p>
              <small>{issue.suggestedFix}</small>
            </div>
          ))}
        </div>
      )}
      {requirements.length > 0 && (
        <div className="reliability-section">
          <strong>Requirements</strong>
          <div className="reliability-table">
            {requirements.map((item) => (
              <div key={item.id}>
                <span>{item.status}</span>
                <p>{item.requirement}</p>
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
                <p>{claim.text}</p>
              </div>
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

function supportLabel(level) {
  return {
    contradicted: "Contradicted",
    none: "Unsupported",
    not_evaluable: "No evidence",
    strong: "Supported",
    weak: "Weak",
  }[level] || level;
}

export default ReliabilityPanel;
