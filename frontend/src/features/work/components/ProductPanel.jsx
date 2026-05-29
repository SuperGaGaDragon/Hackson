/*
Created at: 2026-05-26
Created by: Codex
Last Modified at: 2026-05-29
Last Modified by: Codex
*/
import { CheckCircle2, CircleAlert, FileText, History } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { sortByCreatedAt } from "./eventDisplay";
import { formatEasternTime } from "./timeFormat";

const DELIVERABLE_KINDS = new Set(["text", "chapter", "draft", "revision", "final", "mission_result"]);
const NON_DELIVERABLE_ROLES = new Set(["outline", "review", "reliability_report", "discussion", "search_summary"]);

function ProductPanel({ artifactIndex = [], artifacts = [], mission = null, onLoadArtifact, products = [] }) {
  const viewModel = useMemo(
    () => buildProductView(products, artifacts, artifactIndex),
    [products, artifacts, artifactIndex],
  );
  const [selectedProductId, setSelectedProductId] = useState(null);
  const [selectedArtifactId, setSelectedArtifactId] = useState("all");
  const [loadingArtifactId, setLoadingArtifactId] = useState("");
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

  useEffect(() => {
    if (selectedArtifactId === "all") return;
    if (productArtifacts.some((artifact) => artifact.id === selectedArtifactId)) return;
    setSelectedArtifactId("all");
  }, [productArtifacts, selectedArtifactId]);

  async function selectArtifact(artifactId) {
    setSelectedArtifactId(artifactId);
    const artifact = productArtifacts.find((item) => item.id === artifactId);
    if (!artifact || artifact.loaded || !onLoadArtifact) return;
    setLoadingArtifactId(artifactId);
    try {
      await onLoadArtifact(artifactId);
    } finally {
      setLoadingArtifactId("");
    }
  }

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
                      <small>{productArtifacts.length} entries</small>
                    </span>
                  </button>
                )}
                {productArtifacts.map((artifact, index) => (
                  <button
                    className={artifact.id === selectedArtifactId ? "artifact-nav-row active" : "artifact-nav-row"}
                    key={artifact.id}
                    onClick={() => selectArtifact(artifact.id)}
                    type="button"
                  >
                    <span className="artifact-nav-index">{index + 1}</span>
                    <span className="artifact-nav-copy">
                      <strong>{artifact.title}</strong>
                      <small>
                        {artifact.label}
                        {artifact.createdAt ? ` / ${formatEasternTime(artifact.createdAt)}` : ""}
                      </small>
                    </span>
                  </button>
                ))}
              </nav>
            )}
            <div className="artifact-content">
              {readerArtifacts.length > 0 ? (
                readerArtifacts.map((artifact) => (
                  <ArtifactSection
                    artifact={artifact}
                    key={artifact.id}
                    loading={loadingArtifactId === artifact.id}
                    onLoadArtifact={onLoadArtifact}
                  />
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
          <ArtifactMeta artifact={artifact} compact />
        </div>
        {artifact.label && <small>{artifact.label}</small>}
      </div>
      {mission?.status === "blocked" && (
        <div className="deliverable-blocker">
          <strong>Blocked</strong>
          <p>{mission.lastError || "Needs a decision before this can be verified as final."}</p>
        </div>
      )}
      <div className="deliverable-content">
        <p>{artifact.content || artifact.summary || product?.summary || ""}</p>
      </div>
    </section>
  );
}

function ArtifactSection({ artifact, loading, onLoadArtifact }) {
  const hasContent = Boolean(artifact.content);
  async function load() {
    await onLoadArtifact?.(artifact.id);
  }
  return (
    <section className="artifact-section">
      <div className="artifact-section-head">
        <div>
          <h3>{artifact.title}</h3>
          <ArtifactMeta artifact={artifact} />
        </div>
        {!hasContent && (
          <button className="artifact-load-button" disabled={loading} onClick={load} type="button">
            {loading ? "Loading" : "Open"}
          </button>
        )}
      </div>
      {hasContent ? <p>{artifact.content}</p> : <p className="muted">{artifact.summary || "Open to read this artifact."}</p>}
      <TechnicalDetails artifact={artifact} />
    </section>
  );
}

function ArtifactMeta({ artifact, compact = false }) {
  const items = [artifact.label || artifactLabel(artifact)];
  if (!compact && artifact.createdAt) items.push(formatEasternTime(artifact.createdAt));
  if (!compact && artifact.loaded === false) items.push("Index only");
  return <small className="artifact-meta">{items.filter(Boolean).join(" / ")}</small>;
}

function TechnicalDetails({ artifact }) {
  const metadata = artifact.metadata || {};
  const values = [
    ["Artifact", artifact.id],
    ["Kind", artifact.kind],
    ["Role", artifact.artifactRole || metadata.artifactRole],
    ["Product", artifact.productId || metadata.productId],
    ["Revision of", metadata.revisionOf],
    ["Window", metadata.workWindowId],
    ["Operation", metadata.operation],
  ].filter(([, value]) => value);
  if (values.length === 0) return null;
  return (
    <details className="artifact-technical">
      <summary>Technical details</summary>
      <dl>
        {values.map(([label, value]) => (
          <div key={label}>
            <dt>{label}</dt>
            <dd>{String(value)}</dd>
          </div>
        ))}
      </dl>
    </details>
  );
}

function artifactLabel(artifact) {
  if (artifact.label) return artifact.label;
  const role = artifact.artifactRole || artifact.metadata?.artifactRole;
  if (role === "review") return "Review";
  if (role === "discussion") return "Discussion";
  if (role === "search_summary") return "Search notes";
  if (role === "reliability_report") return "Quality report";
  if (role === "final") return "Final";
  if (artifact.kind === "revision") return "Revision";
  if (artifact.kind === "draft") return "Draft";
  if (artifact.kind === "chapter") return "Chapter";
  if (artifact.kind === "outline") return "Outline";
  if (artifact.kind === "report") return "Report";
  return "Artifact";
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

function buildProductView(products, artifacts, artifactIndex) {
  const artifactById = new Map(artifacts.map((artifact) => [artifact.id, normalizeArtifact(artifact, null)]));
  const indexById = new Map(artifactIndex.map((item) => [item.id, normalizeArtifact(artifactById.get(item.id), item)]));
  const orphanArtifacts = artifacts.filter((artifact) => !artifact.metadata?.productId);
  const productViews = products.map((product) => {
    const productIndexItems = artifactIndex.filter((item) => item.productId === product.id);
    const orderedIds = uniqueIds([
      ...(product.artifactIds || []),
      ...productIndexItems.map((item) => item.id),
      product.deliverableArtifactId,
      product.latestArtifactId,
    ]);
    let productArtifacts = orderedIds.map((artifactId) => indexById.get(artifactId) || artifactById.get(artifactId)).filter(Boolean);
    if (productArtifacts.length === 0) {
      productArtifacts = sortByCreatedAt(artifacts.filter((artifact) => artifact.metadata?.productId === product.id)).map((artifact) =>
        normalizeArtifact(artifact, null),
      );
    }
    const deliverableArtifact =
      (product.deliverableArtifactId && (indexById.get(product.deliverableArtifactId) || artifactById.get(product.deliverableArtifactId))) ||
      newestDeliverableArtifact(productArtifacts);
    return {
      ...product,
      artifacts: sortByCreatedAt(productArtifacts),
      deliverableArtifact,
      latestArtifact:
        (product.latestArtifactId && (indexById.get(product.latestArtifactId) || artifactById.get(product.latestArtifactId))) ||
        productArtifacts[productArtifacts.length - 1] ||
        null,
    };
  });
  if (productViews.length === 0 && orphanArtifacts.length > 0) {
    const orphanStack = sortByCreatedAt(orphanArtifacts).map((artifact) => normalizeArtifact(artifact, null));
    productViews.push({
      id: "artifact-stack",
      title: "Product",
      summary: "",
      status: "active",
      artifacts: orphanStack,
      deliverableArtifact: newestDeliverableArtifact(orphanStack),
      latestArtifact: orphanStack.at(-1) || null,
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

function normalizeArtifact(artifact, indexItem) {
  const source = artifact || {};
  const metadata = { ...(indexItem?.metadata || {}), ...(source.metadata || {}) };
  return {
    ...indexItem,
    ...source,
    artifactRole: source.artifactRole || indexItem?.artifactRole || metadata.artifactRole,
    content: source.content || "",
    createdAt: source.createdAt || indexItem?.createdAt || null,
    kind: source.kind || indexItem?.kind || "other",
    label: indexItem?.label || artifactLabel({ ...source, artifactRole: indexItem?.artifactRole, metadata }),
    loaded: Boolean(source.content) || Boolean(indexItem?.loaded),
    metadata,
    productId: source.metadata?.productId || indexItem?.productId || metadata.productId,
    summary: indexItem?.summary || source.metadata?.summary || source.metadata?.changeSummary || "",
    title: source.title || indexItem?.title || "Untitled artifact",
  };
}

function uniqueIds(values) {
  const seen = new Set();
  return values.filter((value) => {
    if (!value || seen.has(value)) return false;
    seen.add(value);
    return true;
  });
}

function newestDeliverableArtifact(items) {
  return sortByCreatedAt(items).filter((artifact) => isDeliverableArtifact(artifact)).at(-1) || null;
}

function isDeliverableArtifact(artifact) {
  const role = artifact.artifactRole || artifact.metadata?.artifactRole;
  if (role && NON_DELIVERABLE_ROLES.has(role)) return false;
  if (artifact.deliverable) return true;
  if (role === "final") return true;
  if (role && ["draft", "revision", "chapter", "mission_result"].includes(role)) return true;
  return DELIVERABLE_KINDS.has(artifact.kind);
}

export default ProductPanel;
