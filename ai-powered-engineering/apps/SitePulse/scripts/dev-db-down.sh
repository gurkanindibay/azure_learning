#!/usr/bin/env bash
# Stop SitePulse PostgreSQL development environment
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="${SCRIPT_DIR}/../backend"

echo "🛑 Stopping SitePulse database containers..."
cd "${BACKEND_DIR}"
docker compose down

echo "✅ Environment stopped cleanly."
