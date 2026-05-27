/*
Created at: 2026-05-26
Created by: Codex
Last Modified at: 2026-05-26
Last Modified by: Codex
*/
function ProductPanel({ events }) {
  const products = events.filter((event) => event.type === "PRODUCT_UPDATED" || event.type === "MISSION_COMPLETED");
  const latest = products[products.length - 1];
  const payload = latest?.payload || {};

  return (
    <div className="work-card product-panel">
      <div className="card-head">
        <p className="eyebrow">Product</p>
        <span>{payload.tests || "V0"}</span>
      </div>
      {!latest && <p className="muted">No product</p>}
      {latest && (
        <div className="product-body">
          <h2>{latest.title}</h2>
          <p>{payload.summary || latest.message}</p>
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
