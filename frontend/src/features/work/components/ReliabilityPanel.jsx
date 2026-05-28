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
        {Object.entries(report.issueCounts || {}).map(([severity, count]) => (
          <span key={severity}>
            {count} {severity}
          </span>
        ))}
        <span>{evidence.length} evidence</span>
        {issues.length === 0 && <span>Clear</span>}
      </div>
      <div className="reliability-evidence">
        <span>Evidence ledger</span>
        <strong>{evidence.length ? `${evidence.length} sources` : "No trace evidence"}</strong>
      </div>
      {topIssues.length > 0 && (
        <div className="reliability-section">
          <strong>Issues</strong>
          {topIssues.map((issue) => (
            <div className={`reliability-issue severity-${issue.severity}`} key={issue.id}>
              <span>{issue.severity}</span>
              <p>{issue.title}</p>
              {issue.description && <small>{issue.description}</small>}
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
