# Graph Report - dim-rim  (2026-11-18)

## Corpus Check
- 152 files · ~46,056 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 20 file(s) not represented in the graph (top: (none) 8, .example 2, .tsbuildinfo 2)

## Summary
- 1351 nodes · 2725 edges · 99 communities (43 shown, 56 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 208 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `6d535a9f`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- TMNA Disruption Manager RIM MVP
- test_pipeline_migration_parity.py
- EmailAttachment
- .validate_vin
- datetime
- test_smoke.py
- devDependencies
- Chip
- AuditService
- compilerOptions
- compilerOptions
- models.ts
- dim-rim-backend
- scripts
- tsconfig.json
- VinValidationResultRepository
- IntakeCase
- .record_event
- TASK-3 Handoff: Backend Feature B1 - Intake and Classification
- ClassificationService
- VinReviewPage.tsx
- uuid
- uuid
- vin_schemas.py
- steps
- environment
- main.py
- TASK-4 Handoff: Backend Feature B2 - Parsing and VIN Extraction
- parsing.py
- lucide-react
- AuditEventsTable.tsx
- vite
- TASK-5 Handoff: Backend Feature B3 - VIN Validation
- AttachmentParserAdapter
- DeterministicRuleEngine
- vins.py
- eslint.config.js
- EmailAttachmentRepository
- package.json
- dependencies
- TestVinValidationService
- App.tsx
- auth.py
- database.py
- AuthService
- ClassificationReviewPage.tsx
- TestVinValidationAcceptance
- VinRecordRepository
- Layout.tsx
- classification.py
- ValidationResult
- register_error_handlers
- InboxSubmissionService
- @playwright/test
- VinProcessingService
- InboxEmail
- record_classification_decision
- submit_inbox_email
- IntakeCaseOut
- start.sh
- Settings
- docker-entrypoint.sh
- stop.sh
- test_post_decision_nonexistent_case_returns_400
- test_parse_attachment_not_found
- test_extract_vins_case_not_found
- test_get_vin_summary_case_not_found

## God Nodes (most connected - your core abstractions)
1. `IntakeCase` - 69 edges
2. `EmailAttachment` - 39 edges
3. `CandidateRow` - 33 edges
4. `VinProcessingService` - 28 edges
5. `VinValidationResultRepository` - 27 edges
6. `AuditService` - 27 edges
7. `Chip()` - 26 edges
8. `ClassificationService` - 25 edges
9. `InboxSubmissionService` - 24 edges
10. `DeterministicRuleEngine` - 24 edges

## Surprising Connections (you probably didn't know these)
- `extract_vins()` --uses--> `VinProcessingService`  [INFERRED]
  backend/app/routers/vins.py → backend/app/services/vin_processing_service.py
- `validate_vins()` --uses--> `VinProcessingService`  [INFERRED]
  backend/app/routers/vins.py → backend/app/services/vin_processing_service.py
- `get_vin_summary()` --uses--> `VinProcessingService`  [INFERRED]
  backend/app/routers/vins.py → backend/app/services/vin_processing_service.py
- `get_vin_records()` --uses--> `VinProcessingService`  [INFERRED]
  backend/app/routers/vins.py → backend/app/services/vin_processing_service.py
- `TestVinValidationIntegration` --uses--> `VinProcessingService`  [INFERRED]
  backend/tests/test_vin_validation_integration.py → backend/app/services/vin_processing_service.py

## Import Cycles
- None detected.

## Communities (99 total, 56 thin omitted)

### Community 0 - "TMNA Disruption Manager RIM MVP"
Cohesion: 0.05
Nodes (39): API Documentation, Apply migrations, Architecture Overview, Authentication Flow, Backend Architecture, Backend Development, Backend Environment Variables, Backend Tests (+31 more)

### Community 1 - "test_pipeline_migration_parity.py"
Cohesion: 0.08
Nodes (20): run_migrations_offline(), run_migrations_online(), _alembic(), _annotation_kind(), _column_kind(), _env_py_text(), _foreign_key(), _has_alembic_version() (+12 more)

### Community 2 - "EmailAttachment"
Cohesion: 0.06
Nodes (22): CandidateRow, EmailAttachment, CandidateRowRepository, AttachmentParsingService, test_submit_non_candidate_raises_error(), test_candidate_row_repository_create(), test_candidate_row_repository_create_many(), test_candidate_row_repository_delete_by_attachment() (+14 more)

### Community 4 - "datetime"
Cohesion: 0.09
Nodes (7): upgrade(), Base, AuditEvent, ClassificationDecision, VinRecord, VinValidationResult, test_get_case_audit_events_returns_events()

### Community 5 - "test_smoke.py"
Cohesion: 0.11
Nodes (9): User, auth_client(), client(), db_session(), _fresh_schema(), test_cors_headers(), test_database_connection(), test_health_check() (+1 more)

### Community 6 - "devDependencies"
Cohesion: 0.12
Nodes (17): devDependencies, autoprefixer@^10.4.20, postcss@^8.4.49, @testing-library/jest-dom@^6.6.3, @testing-library/react@^16.0.1, @types/node@^22.10.2, @types/react@^18.3.12, @types/react-dom@^18.3.1 (+9 more)

### Community 7 - "Chip"
Cohesion: 0.16
Nodes (22): AttachmentStatusCard(), AttachmentStatusCardProps, CandidateRowTable(), CandidateRowTableProps, CaseDetailCard(), CaseDetailCardProps, CaseQueueList(), CaseQueueListProps (+14 more)

### Community 8 - "AuditService"
Cohesion: 0.16
Nodes (3): AuditEventOut, Config, AuditService

### Community 9 - "compilerOptions"
Cohesion: 0.10
Nodes (19): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleDetection, moduleResolution (+11 more)

### Community 10 - "compilerOptions"
Cohesion: 0.12
Nodes (16): compilerOptions, allowImportingTsExtensions, isolatedModules, lib, module, moduleDetection, moduleResolution, noEmit (+8 more)

### Community 11 - "models.ts"
Cohesion: 0.17
Nodes (11): AuditEvent, AuthUser, CandidateRow, ClassificationDecision, EmailAttachment, IntakeCase, LoginRequest, LoginResponse (+3 more)

### Community 14 - "scripts"
Cohesion: 0.29
Nodes (7): scripts, build, dev, lint, preview, test, type-check

### Community 21 - "IntakeCase"
Cohesion: 0.08
Nodes (8): IntakeCase, IntakeCaseRepository, test_post_decision_confirm_accepts_recommendation(), test_post_decision_reject_clears_binding(), test_post_decision_revise_overrides_recommendation(), test_post_decision_without_pending_recommendation_returns_400(), test_post_recommendation_generates_classification(), test_intake_case_repository_crud()

### Community 22 - ".record_event"
Cohesion: 0.07
Nodes (4): AuditWriterAdapter, AuditEventRepository, get_case_audit_events(), test_get_case_events_returns_empty_for_nonexistent_case()

### Community 23 - "TASK-3 Handoff: Backend Feature B1 - Intake and Classification"
Cohesion: 0.06
Nodes (35): Adapters, Audit Domain, Audit Events (5 total), Audit Trail Screen (TASK-7), auth_middleware.py, Authentication & Authorization, Backend Flows, Classification Domain (+27 more)

### Community 24 - "ClassificationService"
Cohesion: 0.10
Nodes (12): ClassificationDecisionRepository, ClassificationDecisionIn, ClassificationService, test_classification_decision_repository_crud(), test_classification_service_with_real_repository(), test_generate_recommendation_creates_pending_decision(), test_generate_recommendation_raises_error_for_nonexistent_case(), test_record_decision_confirm_accepts_recommendation() (+4 more)

### Community 26 - "VinReviewPage.tsx"
Cohesion: 0.15
Nodes (15): BR01RulesCard(), ValidationOutcomeCard(), ValidationOutcomeCardProps, FilterType, VinRecord, VinResultsTable(), VinResultsTableProps, VinRecordWithValidation (+7 more)

### Community 27 - "uuid"
Cohesion: 0.17
Nodes (5): test_get_intake_case_nonexistent_returns_404(), test_get_intake_case_returns_case(), test_post_intake_submission_creates_case(), test_post_intake_submission_non_candidate_returns_400(), test_post_intake_submission_requires_auth()

### Community 28 - "uuid"
Cohesion: 0.06
Nodes (17): seed_database(), test_get_audit_events_requires_auth(), test_get_case_audit_events_empty_returns_empty_list(), test_get_case_events_returns_events_in_order(), test_get_correlation_events_returns_all_events_for_correlation(), test_record_event_creates_audit_record(), test_get_case_returns_none_for_nonexistent(), test_get_candidate_rows_endpoint() (+9 more)

### Community 29 - "vin_schemas.py"
Cohesion: 0.14
Nodes (8): UserOut, Config, VinExtractionRunOut, VinExtractionSummaryOut, VinRecordOut, VinValidationResultOut, VinValidationRunOut, VinValidationSummaryOut

### Community 30 - "steps"
Cohesion: 0.07
Nodes (35): defaults, name, runs-on, steps, run, name, needs, runs-on (+27 more)

### Community 31 - "environment"
Cohesion: 0.07
Nodes (29): BACKEND_HOST, build, driver, environment, ports, volumes, x-preview-port, args (+21 more)

### Community 32 - "main.py"
Cohesion: 0.08
Nodes (4): lifespan(), CorrelationMiddleware, RequestLoggingMiddleware, health_check()

### Community 33 - "TASK-4 Handoff: Backend Feature B2 - Parsing and VIN Extraction"
Cohesion: 0.08
Nodes (25): Acceptance Tests, Authentication, Backend Flows, Error Handling, Extraction Errors, GET /api/v1/parsing/cases/{case_id}/rows, GET /api/v1/vins/cases/{case_id}/summary, Implemented Endpoints (+17 more)

### Community 34 - "parsing.py"
Cohesion: 0.16
Nodes (5): get_case_candidate_rows(), parse_attachment(), AttachmentParseRequest, AttachmentParseResultOut, CandidateRowOut

### Community 36 - "lucide-react"
Cohesion: 0.15
Nodes (9): CorrelationSummaryCard(), CorrelationSummaryCardProps, BreadcrumbItem, Breadcrumbs(), BreadcrumbsProps, Step, StepperProps, AuditEventOut (+1 more)

### Community 37 - "AuditEventsTable.tsx"
Cohesion: 0.17
Nodes (9): ActionFilterType, ActorFilterType, AuditEvent, AuditEventsTable(), AuditEventsTableProps, ExtractionSummaryTiles(), ExtractionSummaryTilesProps, @testing-library/react (+1 more)

### Community 38 - "vite"
Cohesion: 0.40
Nodes (4): vite@^6.0.1, @vitejs/plugin-react@^4.3.4, vite, @vitejs/plugin-react

### Community 39 - "TASK-5 Handoff: Backend Feature B3 - VIN Validation"
Cohesion: 0.07
Nodes (27): Acceptance Tests, Adapters, Audit Events, Backend Flows, BR-01 VIN Validation Rules, Case CASE-2026-001 VIN Records, Database Schema, Demo Usage (+19 more)

### Community 50 - "vins.py"
Cohesion: 0.18
Nodes (5): get_correlation_id(), extract_vins(), get_vin_records(), get_vin_summary(), validate_vins()

### Community 51 - "eslint.config.js"
Cohesion: 0.18
Nodes (10): @eslint/js@^9.15.0, eslint-plugin-react-hooks@^5.0.0, eslint-plugin-react-refresh@^0.4.14, globals@^15.12.0, typescript-eslint@^8.15.0, @eslint/js, eslint-plugin-react-hooks, eslint-plugin-react-refresh (+2 more)

### Community 53 - "package.json"
Cohesion: 0.15
Nodes (12): eslint@^9.15.0, jsdom@^25.0.1, tailwindcss@^3.4.15, engines, node, name, private, type (+4 more)

### Community 54 - "dependencies"
Cohesion: 0.20
Nodes (10): dependencies, clsx@^2.1.1, lucide-react@^0.454.0, react@^18.3.1, react-dom@^18.3.1, react-router-dom@^6.28.0, tailwind-merge@^2.5.4, clsx (+2 more)

### Community 56 - "App.tsx"
Cohesion: 0.26
Nodes (6): App(), RequireAuth(), RequireAuthProps, AuditTrailPage(), LoginPage(), react-router-dom

### Community 57 - "auth.py"
Cohesion: 0.07
Nodes (11): create_access_token(), decode_access_token(), hash_password(), verify_password(), get_current_user(), get_current_user(), get_current_user_info(), login() (+3 more)

### Community 58 - "database.py"
Cohesion: 0.12
Nodes (3): get_db(), set_sqlite_pragma(), require_role()

### Community 60 - "ClassificationReviewPage.tsx"
Cohesion: 0.32
Nodes (9): ClassificationRecommendationCard(), ClassificationRecommendationCardProps, DecisionForm(), DecisionFormProps, ClassificationReviewPage(), ClassificationDecisionIn, ClassificationDecisionOut, ClassificationRecommendationOut (+1 more)

### Community 62 - "VinRecordRepository"
Cohesion: 0.17
Nodes (6): VinRecordRepository, test_vin_record_repository_count_by_extraction_status(), test_vin_record_repository_count_duplicates(), test_vin_record_repository_create(), test_vin_record_repository_create_many(), test_vin_record_repository_get_by_case()

### Community 63 - "Layout.tsx"
Cohesion: 0.39
Nodes (5): Header(), Layout(), LayoutProps, Sidebar(), SidebarProps

### Community 65 - "classification.py"
Cohesion: 0.24
Nodes (4): ClassificationDecisionOut, Config, ClassificationRecommendationOut, Config

### Community 70 - "InboxSubmissionService"
Cohesion: 0.22
Nodes (7): InboxSubmissionIn, InboxSubmissionService, test_intake_service_with_real_repository(), test_get_case_returns_case(), test_submit_duplicate_email_returns_existing_case(), test_submit_inbox_email_creates_attachment_placeholder(), test_submit_inbox_email_creates_case()

### Community 78 - "IntakeCaseOut"
Cohesion: 0.22
Nodes (4): AttachmentOut, Config, IntakeCaseOut, Config

### Community 80 - "start.sh"
Cohesion: 0.48
Nodes (6): check_prerequisites(), DATABASE_URL, find_available_port(), native_path(), port_in_use(), start.sh script

## Knowledge Gaps
- **2 isolated node(s):** `dim-rim-backend`, `DATABASE_URL`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 673 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **56 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `IntakeCase` connect `IntakeCase` to `EmailAttachment`, `datetime`, `InboxSubmissionService`, `ClassificationService`, `uuid`, `TestVinValidationAcceptance`, `VinRecordRepository`?**
  _High betweenness centrality (0.036) - this node is a cross-community bridge._
- **What connects `dim-rim-backend`, `DATABASE_URL` to the rest of the system?**
  _2 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `TMNA Disruption Manager RIM MVP` be split into smaller, more focused modules?**
  _Cohesion score 0.05 - nodes in this community are weakly interconnected._
- **Why does `VinProcessingService` connect `VinProcessingService` to `.get_validation_summary`, `EmailAttachment`, `datetime`, `.get_by_case_id`, `vins.py`, `VinValidationResultRepository`, `TestVinValidationService`, `uuid`?**
  _High betweenness centrality (0.030) - this node is a cross-community bridge._
- **Should `test_pipeline_migration_parity.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08461538461538462 - nodes in this community are weakly interconnected._
- **Why does `DeterministicRuleEngine` connect `DeterministicRuleEngine` to `.validate_vin`, `datetime`, `VinProcessingService`, `.normalize_vin`, `.get_check_digit`, `.validate_checksum`?**
  _High betweenness centrality (0.030) - this node is a cross-community bridge._
- **Should `EmailAttachment` be split into smaller, more focused modules?**
  _Cohesion score 0.06418219461697723 - nodes in this community are weakly interconnected._