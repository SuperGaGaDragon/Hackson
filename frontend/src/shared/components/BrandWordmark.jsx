/*
Created at: 2026-10-19
Created by: Codex
Last Modified at: 2026-10-19
Last Modified by: Codex
*/

function BrandWordmark({ className = "", href = "", onClick }) {
  const classes = `brand-wordmark ${href ? "brand-wordmark-link" : ""} ${className}`.trim();
  if (href) {
    return (
      <a className={classes} href={href} onClick={onClick}>
        Parallax
      </a>
    );
  }
  return <span className={classes}>Parallax</span>;
}

export default BrandWordmark;
