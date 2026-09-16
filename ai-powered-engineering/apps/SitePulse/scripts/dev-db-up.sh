#!/usr/bin/env bash
# Start SitePulse PostgreSQL 16 development database & Adminer web client
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="${SCRIPT_DIR}/../backend"

echo "🚀 Starting SitePulse PostgreSQL 16 & Adminer..."
cd "${BACKEND_DIR}"
docker compose up -d postgres adminer

echo "⏳ Waiting for PostgreSQL to be healthy..."
docker compose exec postgres pg_isready -U sitepulse_user -d sitepulse -t 30

echo "✅ PostgreSQL is ready on port 5432!"
echo "   Database: sitepulse"
echo "   User:     sitepulse_user"
echo "   Password: sitepulse_secret"
echo ""
echo "📊 Adminer Web Database GUI available at: http://localhost:8081"
