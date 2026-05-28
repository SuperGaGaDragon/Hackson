#!/usr/bin/env bash
# Created at: 2026-05-28
# Created by: Codex
# Last Modified at: 2026-05-28
# Last Modified by: Codex
#
# Zip the latest Desktop Pet app into the frontend dist download path.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP_PATH="${ROOT_DIR}/desktop/src-tauri/target/release/bundle/macos/Hackson Pet.app"
DIST_DOWNLOAD_DIR="${ROOT_DIR}/frontend/dist/assets/downloads"
DIST_DOWNLOAD_PATH="${DIST_DOWNLOAD_DIR}/hackson-pet-mac-arm64.zip"

mkdir -p "${DIST_DOWNLOAD_DIR}"
find "${ROOT_DIR}/frontend/dist/assets" -name README.md -delete

if [[ ! -d "${APP_PATH}" ]]; then
  echo "desktop_app_missing:${APP_PATH}" >&2
  exit 1
fi

rm -f "${DIST_DOWNLOAD_PATH}"
(cd "$(dirname "${APP_PATH}")" && ditto -c -k --sequesterRsrc --keepParent "$(basename "${APP_PATH}")" "${DIST_DOWNLOAD_PATH}")
ls -lh "${DIST_DOWNLOAD_PATH}"
