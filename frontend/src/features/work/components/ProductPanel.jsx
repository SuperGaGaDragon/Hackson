/*
Created at: 2026-05-26
Created by: Codex
Last Modified at: 2026-05-27
Last Modified by: Codex
*/
function ProductPanel({ artifacts = [], products = [] }) {
  const artifactById = new Map(artifacts.map((artifact) => [artifact.id, artifact]));
  const finalProduct = products.find((product) => product.status === "final") || products[0] || null;
  const productArtifacts = finalProduct
    ? finalProduct.artifactIds.map((artifactId) => artifactById.get(artifactId)).filter(Boolean)
    : artifacts;
  const latestArtifact =
    (finalProduct?.latestArtifactId && artifactById.get(finalProduct.latestArtifactId)) || productArtifacts[0] || null;
  const title = finalProduct?.title || latestArtifact?.title || "Product";
  const content = latestArtifact?.content || finalProduct?.summary || "No product";

  return (
    <div className="work-card product-panel">
      <div className="card-head">
        <p className="eyebrow">Product</p>
        <span>{finalProduct?.status || latestArtifact?.kind || "empty"}</span>
      </div>
      {!finalProduct && !latestArtifact && <p className="muted">No product</p>}
      {(finalProduct || latestArtifact) && (
        <div className="product-body">
          <h2>{title}</h2>
          {finalProduct?.summary && <p className="muted">{finalProduct.summary}</p>}
          {productArtifacts.length > 0 && (
            <div className="file-list">
              {productArtifacts.map((artifact) => (
                <span key={artifact.id}>{artifact.kind}</span>
              ))}
            </div>
          )}
          <p className="artifact-content">{content}</p>
        </div>
      )}
    </div>
  );
}

export default ProductPanel;
