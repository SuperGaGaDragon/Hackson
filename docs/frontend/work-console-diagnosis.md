## header
Created at: 2026-05-27
Created by: Codex
Last Modified at: 2026-05-27
Last Modified by: Codex

## brief intro
- goal for this file.
  - Diagnose and fix the public Work Console issue where completed mission progress appears visually covered and terminal missions still show a startable action.
- 架构思路
  - Treat the public domain as the product surface: reproduce on `https://hackson.catachess.com/`, fix locally, build, then copy the verified frontend build to the target public `frontend/dist`.
  - Do not invent Work features beyond current `/api/work` APIs.

## observed issue
- Public Work mission detail can show `Summary` visually over the `Progress` rows.
- A completed Mission still renders an enabled `Start` button, which implies the user can rerun work that has already reached `completed`.
- The screenshot is on `https://hackson.catachess.com/`, so verification must happen on the public-domain build, not only a local Vite port or smoke port.

## ranked hypotheses
- H1: `mission-content` uses a two-column CSS grid with implicit rows, and the full-width `timeline-card` can visually overlap the next grid row when its event list grows.
- H2: `MissionHeader` gates `Start` with only `running` and `stopping`, so terminal states such as `completed` keep the primary action enabled.
- H3: The public domain is serving an older frontend asset even after local fixes, so browser-visible behavior diverges from local code.
- H4: A cached browser asset can keep the old layout until the `index.html` asset hash changes or cache is disabled in verification.

## product fix plan
- Keep Work Console as one clear vertical mission stream: Progress, Summary, Product, Raw Log. This avoids grid-row collision and reads like an operational log.
- Keep the side rails independent. Left rail owns Projects, Agents, and Missions. Right rail owns Inspector and Warning.
- Keep terminal mission actions honest: `Start` is disabled when the selected Mission is `completed`, `running`, or `stopping`.
- Use short existing UI copy only.

## verification
- Before fix: browser script on public domain must capture whether `Summary` overlaps `Progress` and whether completed `Start` is enabled.
- After fix: browser script on public domain must show `Summary` starts below `Progress`, no card intersections, completed `Start` disabled, `/health` OK, and no failed public asset load.

## result
- Before fix, public asset was `/assets/index-DGOMmalo.js`; a completed Mission rendered `Start` as enabled.
- The public static build was updated without restarting the target service.
- After fix, public assets are `/assets/index-O85af_uy.js` and `/assets/index-BNnrJWzs.css`.
- Browser smoke on `https://hackson.catachess.com/` verified:
  - Progress rows: `5`.
  - Summary overlaps Progress: `false`.
  - Summary overlapping Progress rows: `0`.
  - Summary below Progress: `true`.
  - Product below Summary: `true`.
  - Completed `Start` disabled: `true`.
  - Failed resources: `0`.
- Screenshot: `/tmp/hackson_work_public_final.png`.
- Backend Work remains the current V0 deterministic worker; this frontend fix makes the existing event trace visible and honest but does not add new worker capabilities.
