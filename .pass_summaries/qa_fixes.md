# QA Fixes Pass Summary

## Test Counts

### BEFORE (Pipeline Measurement)
- **pytest**: 176 passed, 0 failed, 0 errors, 0 skipped, 176 collected
- **vitest**: 20 passed, 0 failed, 0 errors, 0 skipped, 20 collected
- **playwright**: Not measured (prior E2E pass reported 9 passing but no XML in pipeline count)
- **TOTAL**: 196 passed, 0 not passing, 196 collected

### AFTER (This Pass)
- **pytest**: 176 passed, 0 failed, 0 errors, 0 skipped, 176 collected (not re-run per instructions, pipeline will measure)
- **vitest**: 20 passed, 0 failed, 0 errors, 0 skipped, 20 collected (not re-run per instructions, pipeline will measure)
- **playwright**: 9 passed, 0 failed, 0 errors, 0 skipped, 9 collected
- **TOTAL**: 205 passed, 0 not passing, 205 collected

## Root Cause: Hardcoded Port Numbers

The prior E2E pass used ports 9100 (backend) and 5200 (frontend). This QA pass used different ports (9420/5220) to avoid conflicts with leftover processes, but the test code had hardcoded URLs pointing to the old ports.

### Product Defects Fixed

#### 1. Test helper hardcoded backend and frontend ports
**Files changed**: `/repos/dim-rim/tests/e2e/test-helpers.ts`

The `loginAndSetToken` helper had hardcoded URLs:
- `http://127.0.0.1:9100/api/v1/auth/login` (backend)
- `http://127.0.0.1:5200/login` (frontend)

**Fix**: Made ports configurable via environment variables `BACKEND_PORT` and `FRONTEND_PORT`, with defaults to 9420/5220.

#### 2. Auth spec hardcoded backend port
**Files changed**: `/repos/dim-rim/tests/e2e/auth.spec.ts`

The logout test had a hardcoded API call to `http://127.0.0.1:9100/api/v1/auth/login`.

**Fix**: 
- Updated to use `process.env.BACKEND_PORT || '9420'`
- Changed all `page.goto()` calls to use relative URLs (e.g., `/login` instead of `http://127.0.0.1:5200/login`) so they use the baseURL from playwright.config.ts

#### 3. Navigation spec hardcoded frontend port
**Files changed**: `/repos/dim-rim/tests/e2e/navigation.spec.ts`

All navigation tests had hardcoded URLs like `http://127.0.0.1:5200/intake`.

**Fix**: Changed all `page.goto()` calls to use relative URLs (e.g., `/intake` instead of `http://127.0.0.1:5200/intake`) so they use the baseURL from playwright.config.ts.

#### 4. Playwright config hardcoded frontend port
**Files changed**: `/repos/dim-rim/playwright.config.ts`

The baseURL was hardcoded to `http://127.0.0.1:5200`.

**Fix**: Updated to use template literal with `process.env.FRONTEND_PORT || '5220'`.

## Verification Results

### Services Started Successfully
- Backend: uvicorn running on http://127.0.0.1:9420 (PID 296768)
- Frontend: Vite dev server running on http://127.0.0.1:5220 (PID 296775)

### Playwright E2E Tests: 9 passed
All tests passed on first full run after fixes:

**Authentication (3 tests)**:
- ✓ should login through the form and access protected pages
- ✓ should reject invalid credentials
- ✓ should logout and redirect to login

**Navigation (6 tests)**:
- ✓ should display Intake Cases page at root
- ✓ should display Intake Cases page at /intake
- ✓ should redirect /classification to /intake
- ✓ should redirect /vin-review to /intake
- ✓ should redirect /audit to /intake
- ✓ should redirect unknown paths to root

### Machine-Readable Results
- `/repos/dim-rim/.verification/playwright.xml` (9 tests, 1592 bytes)
- `/repos/dim-rim/.verification/pytest.xml` (176 tests, 34714 bytes, from prior pass)
- `/repos/dim-rim/.verification/vitest.xml` (20 tests, 5635 bytes, from prior pass)

## Failures That Remain
None — all tests pass.

## Assertions or Specs Changed
None. The fixes made the tests properly configurable without changing their assertions or behavior. The changes allow tests to run against any backend/frontend port combination by setting environment variables.

## Cleanup Completed

### Deleted (scaffolding):
- `/repos/dim-rim/backend/_start_server.py`
- `/repos/dim-rim/backend/_stop_server.py`
- `/repos/dim-rim/backend/_server.log`
- `/repos/dim-rim/frontend/_start_frontend.py`
- `/repos/dim-rim/frontend/_stop_frontend.py`
- `/repos/dim-rim/frontend/_frontend.log`
- `/repos/dim-rim/test-results/` (Playwright test artifacts)

### Kept (per instructions):
- `/repos/dim-rim/.verification/` — Contains machine-readable test results (pytest.xml, vitest.xml, playwright.xml)
- `/repos/dim-rim/backend/.venv/` — Python virtual environment (in .gitignore)
- `/repos/dim-rim/backend/app.db` — SQLite database with seed data (in .gitignore)
- `/repos/dim-rim/backend/dev.env` — Development configuration (committed, not in .gitignore)
- `/repos/dim-rim/backend/.env` — Active environment file (in .gitignore)

## Configuration Verified
The application was verified against:
- **Database**: SQLite at `backend/app.db`
- **Backend port**: 9420
- **Frontend port**: 5220
- **Seed data**: 3 demo users, sample cases (loaded from backend seed scripts)

The `dev.env` file exists and is committed, containing the development configuration the backend needs to start (JWT secret, CORS origins, database URL).

## What Was NOT Run
Per instructions, pytest and vitest were not re-run in this pass since the pipeline had just measured them and they showed 0 failures. The pipeline will re-run both suites after this pass to generate final counts.
