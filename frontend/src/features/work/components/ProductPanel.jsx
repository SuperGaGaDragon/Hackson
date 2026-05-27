/*
Created at: 2026-05-26
Created by: Codex
Last Modified at: 2026-05-27
Last Modified by: Codex
*/
function ProductPanel({ artifacts = [], events }) {
  const products = events.filter((event) => event.type === "PRODUCT_UPDATED" || event.type === "MISSION_COMPLETED");
  const latest = products[products.length - 1];
  const latestArtifact = artifacts[0] || null;
  const payload = latest?.payload || {};
  const title = latestArtifact?.title || latest?.title;
  const content = latestArtifact?.content || payload.summary || latest?.message || "No product";

  return (
    <div className="work-card product-panel">
      <div className="card-head">
        <p className="eyebrow">Product</p>
        <span>{latestArtifact?.kind || payload.tests || "V0"}</span>
      </div>
      {!latest && !latestArtifact && <p className="muted">No product</p>}
      {(latest || latestArtifact) && (
        <div className="product-body">
          <h2>{title}</h2>
          <p className="artifact-content">{content}</p>
          <div className="file-list">
            {(payload.changedFiles || []).map((file) => (
              <span key={file}>{file}</span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default ProductPanel;
