#!/bin/bash
# start.sh — Start the TMNA Disruption Manager RIM full-stack application
set -e
trap 'echo "Shutting down..."; [ -f .pids ] && while IFS= read -r pid; do kill "$pid" 2>/dev/null || true; done < .pids; rm -f .pids; exit 0' SIGINT SIGTERM

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Convert paths for native Windows programs under Git Bash
native_path() { if command -v cygpath >/dev/null 2>&1; then cygpath -m "$1"; else printf '%s' "$1"; fi; }

# Port detection (lsof on macOS/Linux, netstat under Git Bash on Windows)
port_in_use() {
    if command -v lsof >/dev/null 2>&1; then
        lsof -iTCP:"$1" -sTCP:LISTEN -t >/dev/null 2>&1
    else
        netstat -an 2>/dev/null | grep -Eq "[:.]$1[[:space:]].*LISTEN"
    fi
}

find_available_port() {
    local port=$1
    while port_in_use "$port"; do
        echo "Port $port in use, trying $((port+1))..." >&2
        port=$((port+1))
    done
    echo $port
}

# === Prerequisite checks ===
check_prerequisites() {
    local errors=0
    echo "=== Checking prerequisites ==="

    # Probe by running it: under Git Bash `python3` may be the Windows Store stub.
    PYTHON=""
    for c in python3 python; do
        if "$c" -c 'import sys' >/dev/null 2>&1; then PYTHON=$c; break; fi
    done
    if [ -n "$PYTHON" ]; then
        PYTHON_VERSION=$("$PYTHON" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
        if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 11 ]); then
            echo "❌ Python 3.11+ required (found $PYTHON_VERSION)"
            errors=$((errors+1))
        else
            echo "✓ Python $PYTHON_VERSION"
        fi
    else
        echo "❌ Python 3 not found. Install from https://python.org"
        errors=$((errors+1))
    fi

    if command -v node &>/dev/null; then
        NODE_VERSION=$(node --version | sed 's/v//')
        NODE_MAJOR=$(echo $NODE_VERSION | cut -d. -f1)
        NODE_MINOR=$(echo $NODE_VERSION | cut -d. -f2)
        if [ "$NODE_MAJOR" -lt 20 ] || ([ "$NODE_MAJOR" -eq 20 ] && [ "$NODE_MINOR" -lt 19 ]); then
            echo "❌ Node.js 20.19+ or 22.12+ required (found $NODE_VERSION)"
            errors=$((errors+1))
        else
            echo "✓ Node.js $NODE_VERSION"
        fi
    else
        echo "❌ Node.js not found. Install from https://nodejs.org"
        errors=$((errors+1))
    fi

    if [ $errors -gt 0 ]; then
        echo "❌ $errors prerequisite(s) missing. Please install them and retry."
        exit 1
    fi
    echo ""
}

check_prerequisites

# Clean up any previous PIDs
if [ -f .pids ]; then
    echo "=== Stopping previous services ==="
    while IFS= read -r pid; do
        if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
            kill "$pid" 2>/dev/null && echo "  Stopped PID $pid" || true
        fi
    done < .pids
    rm -f .pids
    echo ""
fi

# === Backend Setup ===
BACKEND_DIR="$SCRIPT_DIR/backend"
echo "=== Setting up backend ==="
cd "$BACKEND_DIR"

if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment..."
    "$PYTHON" -m venv .venv
fi

# Windows venvs (Git Bash) have Scripts/, macOS/Linux venvs have bin/
if [ -f .venv/Scripts/activate ]; then 
    source .venv/Scripts/activate
else 
    source .venv/bin/activate
fi

echo "Installing backend dependencies..."
pip install . -q

# Copy dev.env to .env if missing
if [ ! -f .env ]; then
    if [ -f dev.env ]; then
        cp dev.env .env
        echo "Created .env from dev.env"
    fi
fi

# Database setup - use absolute path for SQLite
DB_PATH="$BACKEND_DIR/app.db"
export DATABASE_URL="${DATABASE_URL:-sqlite:///$(native_path "$DB_PATH")}"
echo "  Database: $DATABASE_URL"

# Run migrations
echo "Running database migrations..."
python -m alembic upgrade head

# Run seed data
if [ -f app/seed.py ]; then
    echo "Seeding database..."
    python app/seed.py 2>/dev/null || python -c "from app.seed import seed_database; seed_database()" 2>/dev/null || true
fi

# Find available backend port
BACKEND_PORT=$(find_available_port 9000)
echo "Starting backend on http://localhost:$BACKEND_PORT"
uvicorn app.main:app --host 0.0.0.0 --port $BACKEND_PORT &
BACKEND_PID=$!
cd "$SCRIPT_DIR"

# === Frontend Setup ===
FRONTEND_DIR="$SCRIPT_DIR/frontend"
echo ""
echo "=== Setting up frontend ==="
cd "$FRONTEND_DIR"

echo "Installing frontend dependencies..."
npm install --silent

# Find available frontend port
FRONTEND_PORT=$(find_available_port 5173)

# The browser calls a relative /api; vite.config.ts proxies it to BACKEND_PORT
echo "Starting frontend on http://localhost:$FRONTEND_PORT"
BACKEND_PORT="$BACKEND_PORT" npm run dev -- --port "$FRONTEND_PORT" &
FE_PID=$!
cd "$SCRIPT_DIR"

# Save PIDs
echo "$BACKEND_PID" > .pids
echo "$FE_PID" >> .pids

echo ""
echo "=== Services running ==="
echo "  Backend:  http://localhost:$BACKEND_PORT"
echo "  API Docs: http://localhost:$BACKEND_PORT/docs"
echo "  Frontend: http://localhost:$FRONTEND_PORT"
echo ""
echo "=== Demo Seed Credentials ==="
echo "  Disruption Manager:"
echo "    Email:    disruption.mgr@tmna.com"
echo "    Password: Manager123!"
echo ""
echo "  Event Approval Reviewer:"
echo "    Email:    event.reviewer@tmna.com"
echo "    Password: Reviewer123!"
echo ""
echo "  VIP Communication Reviewer:"
echo "    Email:    vip.comms@tmna.com"
echo "    Password: Comms123!"
echo ""
echo "Press Ctrl+C to stop all services"
wait
