/*
Created at: 2026-05-26
Created by: Codex
Last Modified at: 2026-05-29
Last Modified by: Codex
*/
import { CheckCircle2, CircleAlert, FileText, History } from "lucide-react";
import { useMemo, useState } from "react";
import { sortByCreatedAt } from "./eventDisplay";

const DELIVERABLE_KINDS = new Set(["text", "chapter", "draft", "revision", "final", "mission_result"]);
const NON_DELIVERABLE_ROLES = new Set(["outline", "review", "reliability_report", "discussion", "search_summary"]);

function ProductPanel({ artifacts = [], mission = null, products = [] }) {
  const viewModel = useMemo(() => buildProductView(products, artifacts), [products, artifacts]);
  const [selectedProductId, setSelectedProductId] = useState(null);
  const [selectedArtifactId, setSelectedArtifactId] = useState("all");
  const activeProduct =
    viewModel.products.find((product) => product.id === selectedProductId) ||
    viewModel.finalProduct ||
    viewModel.products[0] ||
    null;
  const productArtifacts = activeProduct?.artifacts || [];
  const selectedArtifact =
    selectedArtifactId === "all" ? null : productArtifacts.find((artifact) => artifact.id === selectedArtifactId) || null;
  const allArtifactsSelected = selectedArtifactId === "all" || !selectedArtifact;
  const representativeArtifact = activeProduct?.latestArtifact || productArtifacts[productArtifacts.length - 1] || null;
  const deliverableArtifact = activeProduct?.deliverableArtifact || null;
  const deliveryStatus = activeProduct?.deliveryStatus || (deliverableArtifact ? "draft_candidate" : "none");
  const readerArtifacts = selectedArtifact ? [selectedArtifact] : productArtifacts;
  const title = activeProduct?.title || representativeArtifact?.title || "Product";

  return (
    <div className="work-card product-panel">
      <div className="card-head">
        <p className="eyebrow">Product</p>
        <span>{activeProduct?.status || representativeArtifact?.kind || "empty"}</span>
      </div>
      {!activeProduct && !representativeArtifact && <p className="muted">No product</p>}
      {(activeProduct || representativeArtifact) && (
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
                  onClick={() => {
                    setSelectedProductId(product.id);
                    setSelectedArtifactId("all");
                  }}
                  type="button"
                >
                  <span>{product.title}</span>
                  <small>{product.status}</small>
                </button>
              ))}
            </div>
          )}
          <DeliverableSurface
            artifact={deliverableArtifact}
            deliveryStatus={deliveryStatus}
            mission={mission}
            product={activeProduct}
          />
          {productArtifacts.length > 0 && (
            <div className="product-history-head">
              <span>
                <History size={14} />
                History
              </span>
              <small>{productArtifacts.length}</small>
            </div>
          )}
          <div className="product-reader-shell">
            {productArtifacts.length > 0 && (
              <nav className="artifact-navigator" aria-label="Artifact lineage">
                {productArtifacts.length > 1 && (
                  <button
                    className={allArtifactsSelected ? "artifact-nav-row active" : "artifact-nav-row"}
                    onClick={() => setSelectedArtifactId("all")}
                    type="button"
                  >
                    <span className="artifact-nav-index">All</span>
                    <span className="artifact-nav-copy">
                      <strong>All artifacts</strong>
                      <small>{productArtifacts.length} items</small>
                    </span>
                  </button>
                )}
                {productArtifacts.map((artifact, index) => (
                  <button
                    className={artifact.id === selectedArtifactId ? "artifact-nav-row active" : "artifact-nav-row"}
                    key={artifact.id}
                    onClick={() => setSelectedArtifactId(artifact.id)}
                    type="button"
                  >
                    <span className="artifact-nav-index">{index + 1}</span>
                    <span className="artifact-nav-copy">
                      <strong>{artifact.title}</strong>
                      <small>{artifactLabel(artifact)}</small>
                    </span>
                  </button>
                ))}
              </nav>
            )}
            <div className="artifact-content">
              {readerArtifacts.length > 0 ? (
                readerArtifacts.map((artifact) => (
                  <section className="artifact-section" key={artifact.id}>
                    <h3>{artifact.title}</h3>
                    <ArtifactMeta artifact={artifact} />
                    <p>{artifact.content || artifact.metadata?.summary || ""}</p>
                  </section>
                ))
              ) : (
                <p>{activeProduct?.summary || "No product"}</p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function DeliverableSurface({ artifact, deliveryStatus, mission, product }) {
  const status = deliveryStatus || "none";
  const statusInfo = deliveryStatusInfo(status, mission?.status);
  if (!artifact) {
    return (
      <section className="deliverable-surface empty" aria-label="Authoritative deliverable">
        <div className="deliverable-head">
          <span>
            <FileText size={16} />
            Deliverable
          </span>
          <strong className={`deliverable-status ${statusInfo.tone}`}>{statusInfo.label}</strong>
        </div>
        <p className="muted">No deliverable yet</p>
      </section>
    );
  }
  return (
    <section className={`deliverable-surface ${statusInfo.tone}`} aria-label="Authoritative deliverable">
      <div className="deliverable-head">
        <span>
          {statusInfo.tone === "blocked" ? <CircleAlert size={16} /> : <CheckCircle2 size={16} />}
          Deliverable
        </span>
        <strong className={`deliverable-status ${statusInfo.tone}`}>{statusInfo.label}</strong>
      </div>
      <div className="deliverable-title-row">
        <div>
          <h3>{artifact.title || product?.title || "Deliverable"}</h3>
          <ArtifactMeta artifact={artifact} />
        </div>
        {artifact.kind && <small>{artifactLabel(artifact)}</small>}
      </div>
      {mission?.status === "blocked" && (
        <div className="deliverable-blocker">
          <strong>Blocked</strong>
          <p>{mission.lastError || "Needs a decision before this can be verified as final."}</p>
        </div>
      )}
      <div className="deliverable-content">
        <p>{artifact.content || artifact.metadata?.summary || product?.summary || ""}</p>
      </div>
    </section>
  );
}

function ArtifactMeta({ artifact }) {
  const items = [
    artifact.kind,
    artifact.metadata?.artifactRole,
    artifact.metadata?.verdict ? `verdict ${artifact.metadata.verdict}` : "",
    artifact.metadata?.revisionOf ? `revision of ${artifact.metadata.revisionOf}` : "",
  ].filter(Boolean);
  if (items.length === 0) return null;
  return <small className="artifact-meta">{items.join(" / ")}</small>;
}

function artifactLabel(artifact) {
  if (artifact.metadata?.artifactRole === "review") return "review";
  if (artifact.metadata?.artifactRole === "discussion") return "discussion";
  if (artifact.metadata?.artifactRole === "search_summary") return "search summary";
  if (artifact.metadata?.artifactRole === "final") return "final";
  if (artifact.metadata?.revisionOf) return "revision";
  return artifact.kind;
}

function deliveryStatusInfo(status, missionStatus) {
  if (missionStatus === "blocked" || status === "blocked_candidate") return { label: "Blocked candidate", tone: "blocked" };
  return (
    {
      draft_candidate: { label: "Draft candidate", tone: "draft" },
      none: { label: "No deliverable", tone: "empty" },
      user_accepted: { label: "Accepted", tone: "verified" },
      verified_final: { label: "Verified final", tone: "verified" },
    }[status] || { label: "Draft candidate", tone: "draft" }
  );
}

function buildProductView(products, artifacts) {
  const artifactById = new Map(artifacts.map((artifact) => [artifact.id, artifact]));
  const orphanArtifacts = artifacts.filter((artifact) => !artifact.metadata?.productId);
  const productViews = products.map((product) => {
    const listedArtifacts = (product.artifactIds || []).map((artifactId) => artifactById.get(artifactId)).filter(Boolean);
    const fallbackArtifacts = artifacts.filter((artifact) => artifact.metadata?.productId === product.id);
    const productArtifacts = listedArtifacts.length > 0 ? listedArtifacts : sortByCreatedAt(fallbackArtifacts);
    const deliverableArtifact =
      (product.deliverableArtifactId && artifactById.get(product.deliverableArtifactId)) ||
      newestDeliverableArtifact(productArtifacts);
    return {
      ...product,
      artifacts: productArtifacts,
      deliverableArtifact,
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
      deliverableArtifact: newestDeliverableArtifact(orphanArtifacts),
      latestArtifact: sortByCreatedAt(orphanArtifacts).at(-1) || null,
    });
  }
  return {
    products: productViews,
    finalProduct:
      productViews.find((product) => product.deliveryStatus === "verified_final") ||
      productViews.find((product) => product.status === "final") ||
      productViews.find((product) => product.deliverableArtifact) ||
      null,
  };
}

function newestDeliverableArtifact(items) {
  return sortByCreatedAt(items).filter((artifact) => isDeliverableArtifact(artifact)).at(-1) || null;
}

function isDeliverableArtifact(artifact) {
  const role = artifact.metadata?.artifactRole;
  if (role && NON_DELIVERABLE_ROLES.has(role)) return false;
  if (role === "final") return true;
  if (role && ["draft", "revision", "chapter", "mission_result"].includes(role)) return true;
  return DELIVERABLE_KINDS.has(artifact.kind);
}

export default ProductPanel;
