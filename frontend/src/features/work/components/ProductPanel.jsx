/*
Created at: 2026-05-26
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
*/
import { useMemo, useState } from "react";
import { sortByCreatedAt } from "./eventDisplay";

function ProductPanel({ artifacts = [], products = [] }) {
  const viewModel = useMemo(() => buildProductView(products, artifacts), [products, artifacts]);
  const [selectedProductId, setSelectedProductId] = useState(null);
  const activeProduct =
    viewModel.products.find((product) => product.id === selectedProductId) ||
    viewModel.finalProduct ||
    viewModel.products[0] ||
    null;
  const productArtifacts = activeProduct?.artifacts || [];
  const finalArtifact = activeProduct?.latestArtifact || productArtifacts[productArtifacts.length - 1] || null;
  const renderStack = activeProduct?.status !== "final" && productArtifacts.length > 1;
  const title = activeProduct?.title || finalArtifact?.title || "Product";

  return (
    <div className="work-card product-panel">
      <div className="card-head">
        <p className="eyebrow">Product</p>
        <span>{activeProduct?.status || finalArtifact?.kind || "empty"}</span>
      </div>
      {!activeProduct && !finalArtifact && <p className="muted">No product</p>}
      {(activeProduct || finalArtifact) && (
        <div className="product-body">
          <div className="product-title-row">
            <div>
              <h2>{title}</h2>
              {activeProduct?.summary && <p className="muted">{activeProduct.summary}</p>}
            </div>
            {activeProduct?.status === "final" && <strong className="final-pill">Final</strong>}
          </div>
          {viewModel.products.length > 1 && (
            <div className="product-tabs" aria-label="Product list">
              {viewModel.products.map((product) => (
                <button
                  className={product.id === activeProduct?.id ? "active" : ""}
                  key={product.id}
                  onClick={() => setSelectedProductId(product.id)}
                  type="button"
                >
                  <span>{product.title}</span>
                  <small>{product.status}</small>
                </button>
              ))}
            </div>
          )}
          {productArtifacts.length > 0 && (
            <div className="artifact-lineage" aria-label="Artifact lineage">
              {productArtifacts.map((artifact) => (
                <span className="artifact-row" key={artifact.id}>
                  <strong>{artifact.title}</strong>
                  <small>{artifact.kind}</small>
                </span>
              ))}
            </div>
          )}
          <div className="artifact-content">
            {renderStack ? (
              productArtifacts.map((artifact) => (
                <section className="artifact-section" key={artifact.id}>
                  <h3>{artifact.title}</h3>
                  <p>{artifact.content || artifact.metadata?.summary || ""}</p>
                </section>
              ))
            ) : (
              <p>{finalArtifact?.content || activeProduct?.summary || "No product"}</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

function buildProductView(products, artifacts) {
  const artifactById = new Map(artifacts.map((artifact) => [artifact.id, artifact]));
  const orphanArtifacts = artifacts.filter((artifact) => !artifact.metadata?.productId);
  const productViews = products.map((product) => {
    const listedArtifacts = (product.artifactIds || []).map((artifactId) => artifactById.get(artifactId)).filter(Boolean);
    const fallbackArtifacts = artifacts.filter((artifact) => artifact.metadata?.productId === product.id);
    const productArtifacts = listedArtifacts.length > 0 ? listedArtifacts : sortByCreatedAt(fallbackArtifacts);
    return {
      ...product,
      artifacts: productArtifacts,
      latestArtifact:
        (product.latestArtifactId && artifactById.get(product.latestArtifactId)) ||
        productArtifacts[productArtifacts.length - 1] ||
        null,
    };
  });
  if (productViews.length === 0 && orphanArtifacts.length > 0) {
    productViews.push({
      id: "artifact-stack",
      title: "Product",
      summary: "",
      status: "active",
      artifacts: sortByCreatedAt(orphanArtifacts),
      latestArtifact: sortByCreatedAt(orphanArtifacts).at(-1) || null,
    });
  }
  return {
    products: productViews,
    finalProduct: productViews.find((product) => product.status === "final") || null,
  };
}

export default ProductPanel;
