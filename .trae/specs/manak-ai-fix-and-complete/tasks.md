# MANAK AI Fix & Complete — Implementation Tasks (v2)

**Spec file**: [spec.md](file:///c:/TURBOC3/Projects/Manak%20Ai/.trae/specs/manak-ai-fix-and-complete/spec.md)

## Legend
- **Priority**: high (blocks end-to-end flow), medium (feature-complete), low (polish).
- **TR = Test Requirement**: each task has at least one `rule` or `rubric` TR with pass condition.
- **Status**: pending / in_progress / completed / blocked / cancelled.
- **AC**: parent Acceptance Criterion from spec.md.

---

## Phase 1 — Foundation: Data + Security + Config

## Task 1: Backend Foundation — Security, Config, Logging, DB Init

**Priority**: high  **Status**: pending  **AC**: F1, F16, FR-19, AC-R1, AC-R2

### Scope
- **1.1 Security**: Keep the already-switched direct `bcrypt` implementation (no passlib was causing 3.13 issues). Fix cost factor to >= 12.
- **1.2 Config**: Fix `settings.py`:
  - Parse `CORS_ORIGINS` from comma string → list`; default `["http://localhost:5173","http://localhost:4173"]`.
  - Add new threshold settings: `MIN_SEMANTIC_SIMILARITY=0.45`, `MIN_FINAL_SCORE=0.50`, `MIN_EVIDENCE_CHUNKS=1`, `MAX_LLM_CONTEXT_CHUNKS=5`, all env-overridable.
  - Add `SUPPORTED_LANGS=["en","hi","kn"]`; default `TRANSLATION_PROVIDER=mock`.
  - DEBUG=False mode → raise error on default JWT secrets.
- **1.3 Logging middleware + exception catcher middleware in main.py: catch 500s return generic detail; log traceback via logging.exception; no leak.
- **1.4 DB**: Ensure `init_db.py` imports all models (existing + ConversationMessage, AdminAuditLog already exist. Ensure 22 tables.
- **1.5 Demo admin user in seed_all.

### Files
- [security/auth.py](file:///c:/TURBOC3/Projects/Manak%20Ai/backend/app/security/auth.py)
- [config/settings.py](file:///c:/TURBOC3/Projects/Manak%20Ai/backend/app/config/settings.py)
- [main.py](file:///c:/TURBOC3/Projects/Manak%20Ai/backend/app/main.py)
- [init_db.py](file:///c:/TURBOC3/Projects/Manak%20Ai/backend/init_db.py)
- [models/__init__.py](file:///c:/TURBOC3/Projects/Manak%20Ai/backend/app/models/__init__.py)
- Update `backend/seed_all.py`

### TRs
- **TR-R1.1**: DB `users.password_hash` starts with `$2b$`.
- **TR-R1.2**: `python init_db.py; python seed_all.py` (2 runs) no duplicate errors.
- **TR-R1.3**: 22 tables exist in SQLite (per _tmp_check_tables.py output).
- **TR-R1.4**: `GET /health works; 404 on unknown returns detail; 500-caught-in-middleware route returns generic detail.

---

## Task 2: Expanded DEMO Dataset (Structured Metadata + All Empty Tables Populated)

**Priority**: high  **Status**: pending  **AC**: FR-2, FR-12, FR-13, AC-R2, AC-R3, AC-R8, AC-Ru4, T2/T3 evidence

### Scope
- **2.1 Standards**: Keep 4 existing; add 3 NEW realistic demo BIS-standard placeholders (e.g., IS 2062 (steel), IS 10171 (packaged drinking water — not dairy "curd"), IS 14543 (packaged water)).
- **2.2 Per existing 4 Standards**:
  - ≥ 5 StandardClauses each (with clause_number, clause_title, scope, content).
  - ≥ 8 Requirements per standard (linked to clauses).
  - ≥ 3 Tests + ≥ 1 TestMethod per test.
  - At least 2 standards linked to 1 seeded CertificationScheme.
- **2.3 Labs**: 5 DEMO laboratories (NABL / BIS / GOVT / PRIVATE / INTERNATIONAL), 2 HallmarkingCentre.
- **2.4 3 QCO records (typed via DocumentType QCO) linking at least 1 standard each with UNVERIFIED_DEMO tier (demo certification applicability evidence).
- **2.5 5 FAQs + 3 Circulars + 2 Product Manuals all with full 17-field metadata.
- **2.6 KnowledgeDocument + KnowledgeChunk re-ingestion with structured 17-field metadata.
- **2.7 Every seeded record uses AuthorityLevel=UNVERIFIED_DEMO (or OFFICIAL_BIS only for seeded "standards" when marked DEMO) with consistent authority.

### Files
- `backend/seed_clauses_requirements_tests.py (NEW)
- `backend/seed_labs_hallmarks.py (NEW)
- `backend/seed_faqs_circulars_qcos.py (NEW)
- Update [seed_all.py](file:///c:/TURBOC3/Projects/Manak%20Ai/backend/seed_all.py)
- Update [seed_standards.py](file:///c:/TURBOC3/Projects/Manak%20Ai/backend/seed_standards.py)
- Update [knowledge/ingestion.py](file:///c:/TURBOC3/Projects/Manak%20Ai/backend/app/knowledge/ingestion.py) (17-field metadataschema)

### TRs
- **TR-R2.1**: standards count ≥ 7; standard_clauses ≥ (7*5=35); requirements ≥ 56; tests ≥ 21; labs ≥ 5.
- **TR-R2.2**: Each seeded lab/standard/clause knowledge chunk has 17 metadata fields non-null (or explicitly null).
- **TR-R2.3**: AuthorityLevel not misrepresented (OFFICIAL_BIS only for marked standards only; all other seeded items UNVERIFIED_DEMO; UNVERIFIED_DEMO >= 80%.
- **TR-R2.4**: 2 seeded standard_clause for IS 17342 exist (Clause 4.2 Materials / Clause 4 leak test) → drives tests T2/T3/T6/T7

---

## Task 3: Standards API (List + Detail + Search)

**Priority**: high  **Status**: pending  **AC**: F3, F5, FR-2, FR-12, AC-R3

### Scope
- Schemas: standard.py schemas StandardResponse, StandardDetailResponse, StandardClauseResponse, RequirementResponse, TestResponse.
- Router standards.py: GET /standards?search=&category=&limit=&offset=, GET /standards/:id (clauses, requirements, tests, related_standards (by category), GET /standards/:id/related, PATCH for admin only.
- Wire into api/v1/api.py.

### Files
- New backend/app/schemas/standard.py
- New backend/app/api/v1/standards.py
- Edit [api/v1/api.py](file:///c:/TURBOC3/Projects/Manak%20Ai/backend/app/api/v1/api.py)

### TRs
- **TR-R3.1**: GET standards returns ≥ 7.
- **TR-R3.2**: GET standards/:id for IS 17342 → clauses.length ≥ 5, requirements.length ≥ 8.
- **TR-R3.3**: ?search=Steel returns standards with Steel in scope/title/category.

---

## Task 4: Dashboard Stats API + /me wiring + Admin Endpoints

**Priority**: high  **Status**: pending  **AC**: F2, F14, FR-19, AC-R10, AC-R1, AC-R4.3

### Scope
- Router dashboard.py: GET stats + activity; schemas.
- Router admin.py: GET/PATCH users; POST /reindex; GET /ingestions; GET /analytics; GET /audit-logs; AdminAuditLog writes on role change / ingest / reindex / compliance status change (hooks in ingestion.py, compliance.py, admin router).

### Files
- New schemas/dashboard.py, schemas/admin.py, new api/v1/dashboard.py, api/v1/admin.py, api.py wire.

### TRs
- **TR-R4.1**: GET /dashboard/stats with 0 products → total_products=0, total_standards≥7, total_documents≥6, total_compliance_checks=0.
- **TR-R4.2**: Non-admin GET admin/users → 403.
- **TR-R4.3**: Admin PATCH role → 200, role changed, AdminAuditLog row exists.

---

## Phase 2 — Core Search, Query Understanding & RAG

## Task 5: Query Understanding + Intent Routing (FR-5 / FR-6)

**Priority**: high  **Status**: pending  **AC**: FR-5, FR-6, T1, T3, T8

### Scope
- New enum Intent (12 values) + schemas in `app/ai/query.py`.
- QueryUnderstanding service:
  - cleaning (strip, lower).
  - IS regex, clause regex, location entity regex, product extraction.
  - keyword/synonym dictionary lookup.
  - category mapping to existing ProductCategory enum.
  - deterministic intent classifier (exact IS# forced STANDARD_SEARCH, hallmark→HALLMARKING, lab→LABORATORY; else keyword→GENERAL_BIS/PRODUCT_STANDARD based on keywords "certification", "testing", etc.).
  - synonyms dict for common BIS domain synonyms (bottle ↔ flask/container; "SS" ↔ stainless steel, etc.)
- Intent routing filters in retriever / search pipeline: if LABORATORY skip knowledge search; only labs table.

### Files
- New backend/app/ai/query.py (QueryUnderstanding + Intent enum + synonyms dict)
- Modify rag/engine.py and rag/retriever.py to accept QU object
- Test in api/v1/knowledge.py → call QU parse

### TRs
- **TR-R5.1**: parse "Which BIS standard applies to stainless steel water bottle?" → product="stainless steel water bottle", intent=STANDARD_SEARCH (or PRODUCT_STANDARD), category=CONSUMER_PRODUCTS, is_numbers=[] if not present).
- **TR-R5.2**: parse "IS 17342:2020" → is_numbers=["17342:2020"], intent=STANDARD_SEARCH forced.
- **TR-R5.3**: "hallmarking centre Delhi" → intent=HALLMARKING, location.city=Delhi.
- **TR-R5.4**: "Find accredited electrical lab in Mumbai" → LABORATORY, location=Mumbai; intent forced.

---

## Task 6: Hybrid Search Pipeline (FR-3) + Relevance Threshold (FR-4) + Metadata Filtering

**Priority**: high  **Status**: pending  **AC**: FR-3, FR-4, FR-12, T1, T2, T9

### Scope
- Full 11-step pipeline in RAGEngine (QueryUnderstanding → lexical search + vector search → metadata filtering → candidate union → rerank → threshold → evidence validation).
- Lexical search improvement:
  - Exact IS number substring match → +2.0 boost.
  - Keyword TF-based substring across content, title, standard_number.
  - Threshold drop chunks below similarity 0.45 raw cosine; below final 0.5 reranked score.
  - If 0 candidates pass, straight → no-evidence response without LLM call, answer uses exact FR-4 required sentence + rejected_as_irrelevant flag.
- Reranker deterministic formula from spec.
- Metadata filtering: if extracted is_numbers non-empty → filter standard_number match or chunk. If product_category non-empty → filter metadata. If LABORATORY/HALLMARKING only appropriate table.
- Authority level bonus in rerank (OFFICIAL_BIS +1.2, GOVERNMENT +0.8, VERIFIED_THIRD +0.4, UNVERIFIED_DEMO 0.

### Files
- Modify [rag/engine.py](file:///c:/TURBOC3/Projects/Manak%20Ai/backend/app/rag/engine.py)
- Modify [rag/retriever.py](file:///c:/TURBOC3/Projects/Manak%20Ai/backend/app/rag/retriever.py)
- Modify [api/v1/knowledge.py](file:///c:/TURBOC3/Projects/Manak%20Ai/backend/app/api/v1/knowledge.py)

### TRs
- **TR-R6.1**: Query "curd" → response answer is "No sufficiently relevant authoritative information was found…" (or the other exact sentence); sources.length=0; confidence=INSUFFICIENT_EVIDENCE; rejected_as_irrelevant=true.
- **TR-R6.2**: Query "IS 17342:2020" → top result match metadata contains standard_number="IS 17342:2020" with combined_score >= 1.5+ (from exact IS boost).
- **TR-R6.3**: "mars rover" → confidence=INSUFFICIENT_EVIDENCE (T9).
- **TR-R6.4**: Returned sources in normal query none below raw cosine >= 0.45 (no 0.31 chunk returned).

---

## Task 7: Improved LLM + Evidence-Based Mock (FR-17) + Citations (FR-11)

**Priority**: high  **Status**: pending  **AC**: F11, FR-11, FR-17, AC-R5, AC-Ru2, T8, T9

### Scope
- LLMFactory in `ai/factory.py` + OpenAI provider + ImprovedMock provider.
- ImprovedMock.generate(prompt, context chunks structured output from only the retrieved chunks' first sentences (concatenated; exact insufficient sentence if no chunks.
- OpenAI provider: hallucination check: regex scan generated output for IS numbers not in provided context chunks → replace notifier.
- System prompt prepend exact required FR-17 text.
- RAGEngine response sources now uses Citation fields (standard_number, clause, page, url, version, last_verified, authority).
- Conversation models ConversationMessage.

### Files
- New backend/app/ai/factory.py
- Modify ai/llm.py, ai/embeddings.py, rag/engine.py
- New schemas/chat.py, new api/v1/chat.py, wire in api.py.

### TRs
- **TR-R7.1**: Query "What is IS 9999:2025?" → answer exact insufficient sentence; confidence=INSUFFICIENT_EVIDENCE; No "IS 9999" appears in answer body OR sources (AC-R5).
- **TR-R7.2**: Query about water bottle standards top answer includes substrings from retrieved chunks text (no fixed prefix).
- **TR-R7.3**: POST /chat/sessions, POST messages → createConversationMessage rows.
- **TR-R7.4**: sources[0] includes source_authority (4-tier value).

---

## Phase 3 — Product & Compliance

## Task 8: Product Intelligence Matching (FR-7) + 4-Tier Applicability (FR-13) + Analyze Endpoint

**Priority**: high  **Status**: pending  **AC**: F4, F6, FR-7, FR-13, AC-R4, T3, T6

### Scope
- Extend Product model columns (subcategory, material(str), intended_use(str), industry(str), technical_attributes(JSON), keywords(Text), backward nullable columns to SQLAlchemy. Alembic not needed because we auto-init, but migration files needed for sqlite alter/add columns via add_column in init if missing? No → recreate tables not ok. We'll add columns to existing model class; if DB already created; so init_db will reif exists we need to add).
- New 7-step matcher in product/matching.py replaces old 3-strategy.
- ProductStandardMatch field renamed: `is_mandatory` → `certification_applicability` enum (COMPULSORY, VOLUNTARY, NOT_DETERMINED, EVIDENCE_INSUFFICIENT).
- Rules for certification applicability (FR-13): COMPULSORY only if QCO/scheme with OFFICIAL tier record exists; otherwise max VOLUNTARY/NOT_DETERMINED.
- Explain match_reason structured text.
- POST /products/:id/analyze new endpoint returning match+standard.

### Files
- Modify [models/product.py](file:///c:/TURBOC3/Projects/Manak%20Ai/backend/app/models/product.py)
- Modify [product/matching.py](file:///c:/TURBOC3/Projects/Manak%20Ai/backend/app/product/matching.py)
- Modify [schemas/product.py](file:///c:/TURBOC3/Projects/Manak%20Ai/backend/app/schemas/product.py)
- Modify [api/v1/products.py](file:///c:/TURBOC3/Projects/Manak%20Ai/backend/app/api/v1/products.py)

### TRs
- **TR-R8.1**: "Stainless Steel Water Bottle" match-standards → IS 17342 match_score >= 0.55 + standard.standard_number populated.
- **TR-R8.2**: certification_applicability ≤ VOLUNTARY or NOT_DETERMINED or NOT COMPULSORY for demo data.
- **TR-R8.3**: match_reason includes scope overlap keyword count text.
- **TR-R8.4**: POST /products/:id/analyze → 200 with matches array.

---

## Task 9: Compliance Passport API 6 Statuses + Score (FR-9)

**Priority**: high  **Status**: pending  **AC**: F6, FR-9, AC-R4, AC-R6, T6

### Scope
- New endpoints GET products/:id/compliance/:standard_id/items, PATCH /compliance/items/:item_id, GET products/:id/compliance/summary.
- Auto-create ComplianceCheck row on first GET items if none (seed).
- Status enum NOT_STARTED, IN_PROGRESS, PENDING_VERIFICATION, PARTIALLY_SATISFIED, SATISFIED, UNKNOWN (replace status PENDING/FAILED/PASSED old; need backward compat with existing statuses if exists or add new).
- Score formula exactly from FR-9).
- Rollup status exactly from rules of statuses of checklist
- Summary endpoint returns per-standard with status + score + "Not Yet Assessed" indicator).

### Files
- Modify [product/compliance.py](file:///c:/TURBOC3/Projects/Manak%20Ai/backend/app/product/compliance.py)
- Modify [models/product.py](file:///c:/TURBOC3/Projects/Manak%20Ai/backend/app/models/product.py) (ComplianceCheckItem.status enum)
- Modify schemas/product.py, api/v1/products.py

### TRs
- **TR-R9.1**: Fresh product → GET summary → NOT_STARTED, score "Not Yet Assessed" (null, text).
- **TR-R9.2**: 2 SATISFIED + 1 FAILED items → summary PARTIALLY_SATISFIED score=(2+0)/3=66.7.
- **TR-R9.3**: All items SATISFIED → "Satisfied" status.

---

## Phase 4 — Document, Labs, Graph, Multilingual

## Task 10: Document Analysis Backend (FR-10)

**Priority**: medium  **Status**: pending  **AC**: F7, FR-10, AC-R7

### Scope
- New api router documents.py → POST analyze.
- New app/document/__init__.py + extractor.py txt/pdf/docx/image + analyzer.py entities regexes; 12-step pipeline
- Reject disclaimers always; never "valid" language banned.
- Sanitize filenames (path traversal stripped; store in backend/uploads; allow-list;
- Standards found, entities found; evidence/missing lists; compliance_score computed; compliance_score not fixed value 85;
- Uploads folder created automatically.

### Files
- New backend/app/api/v1/documents.py; backend/app/document/*; schemas/document.py; api.py wire.

### TRs
- **TR-R10.1**: Upload txt with "IS 17342:2020 Clause 4.2 Page 3 → standards_found contains IS 17342:2020, clauses includes 4.2, pages includes 3.
- **TR-R10.2**: Upload txt  + standard_id → compliance_score != 85 != fixed integer).
- **TR-R10.3**: Filename ../../../etc/passwd.pdf sanitized stored under uploads safe name only base.
- **TR-R10.4**: Response includes disclaimer text.

---

## Task 11: Laboratories + Hallmarking API (FR-8 LabMatcher data)

**Priority**: medium  **Status**: pending  **AC**: F8, AC-R8

### Scope
- laboratories.py + schemas/laboratory.py → GET labs, hallmarking centres.
- Filter search, test/standard/city/lab_type/limit/state/offset.
- Responses always show verification_status; DEMO badge fields.

### Files
- New api/v1/laboratories.py, api/v1/hallmarking.py
- New schemas/laboratory.py; api.py wire.

### TRs
- **TR-R11.1**: /laboratories?city=Delhi → returns labs in Delhi count matches).
- **TR-R11.2**: lab_type=NABL filter only NABL labs).
- **TR-R11.3**: Demo source fields present.
- **TR-R11.4**: Empty lab response with 0 results empty.

---

## Task 12: Knowledge Graph API from DB Relationships (FR-14)

**Priority**: medium  **Status**: pending  **AC**: F9, FR-14, AC-R9

### Scope
- New graph.py → /graph/data and node/:id.
- Nodes actual tables; edges actual FK relations capped 500/1500).
- Node click detail endpoint returns full entity data.

### Files
- New api/v1/graph.py, schemas/graph.py, api.py wire.

### TRs
- **TR-R12.1**: nodes >= standards count + clauses count).
- **TR-R12.2**: edges > standards count).
- **TR-R12.3**: /node/lab_id returns lab with capabilities/city data.

---

## Task 13: Multilingual Layer EN/HI/KN (FR-15)

**Priority**: medium  **Status**: pending  **AC**: F10, FR-15

### Scope
- ai/translation.py abstract + MockTranslator dict-based with token preserving placeholder replacements translate; hi/kn translations for nav/answers.
- Search endpoint now accepts lang parameter query lang param or Accept-Language) → translate query EN; translate answer preserving IS/clause/cert numbers.
- lang_fallback flag.

### Files
- New backend/app/ai/translation.py; factory.py wire; rag/engine.py translate; api/knowledge.py; settings.py;

### TRs
- **TR-R13.1**: lang=hi accepted without error (at minimum fallback flag).
- **TR-R13.2**: answer containing IS 17342:2020 preserved; substring retained in translated output (regex check if translator works MockTranslator outputs some words hindi translated; placeholders tests).

---

## Phase 5 — Eval Dataset + Tests

## Task 14: Evaluation Dataset + Retrieval Evaluation Script (FR-16)

**Priority**: medium  **Status**: pending  **AC**: FR-16, AC-Ru5

### Scope
- evaluation_dataset.json ≥40 rows 7 categories).
- eval_retrieval.py runs retrieval pipeline; prints Top-1 Top-5 acc, citation accuracy, No-answer accuracy; groundedness top 10 answerable.

### Files
- New backend/evaluation_dataset.json; backend/eval_retrieval.py

### TRs
- **TR-R14.1**: ≥ 40+ entries covering all 7 categories.
- **TR-R14.2**: Script runs outputting 5 metrics without errors).
- **TR-R14.3**: T1 curd no-answer correctly recognized (No-answer acc ≥90%).
- **TR-R14.4**: 5 rubric score >= 1).

---

## Task 15: pytest Suite

**Priority**: high  **Status**: pending  **AC**: NFR-4

### Scope
- tests/conftest.py in-memory SQLite DB; auth/me/register/login.
- test_auth.py, test_standards_api.py; test_rag (T1 curd, T2 exact IS, T9 unknown).
- test_product_match.py; test_document_analysis; test_lab_api; test_graph_api.

### Files
- New backend/tests/conftest.py; backend/tests/test_*.py

### TRs
- **TR-R15.1**: pytest backend/tests -v tests pass).

---

## Phase 6 — Frontend

## Task 16: Frontend API Client Update + AuthGuard + Refresh

**Priority**: high  **Status**: pending  **AC**: F1, FR-8, FR-19, AC-R1, AC-R10, AC-R11, T4, T5

### Scope
- client: types & calls dashboard stats; new API client methods standards CRUD; compliance items + summary + analyze; documents analyze FormData laboratories; labs/hallmarking; graph; chat sessions; admin; me refresh logout;
- save both tokens; onUnauthorized callback; error detail display HTTP code + detail;
- AuthGuard HOC redirects to /login on no token + me verify;
- App.tsx wrap guards; add routes for /standards /standards/:id /admin.

### Files
- api/client.ts; auth/AuthGuard.tsx; App.tsx

### TRs
- **TR-R16.1**: Fresh browser /dashboard no token → redirect to /login.
- **TR-R16.2**: After login reload → /dashboard stays; refresh token stored.
- **TR-R16.3**: All previous calls backward-compatible existing client signatures preserved).

---

## Task 17: Dashboard Real Data + Language Selector (FR-18 Dashboard + Back arrow)

**Priority**: high  **Status**: pending  **AC**: F2, AC-R10, AC-Ru1

### Scope
- Dashboard use me() name actual full_name actual dashboard stats actual numbers from dashboard stats.
- Admin nav visible for ADMIN only).
- icon fix duplicate Search icon replace Lab icon Laboratory.
- Language selector EN/HI/KN.

### Files
- pages/DashboardPage.tsx; new components/LanguageSelector.tsx; new i18n/dictionary.ts, nav update pages/*

### TRs
- **TR-R17.1**: "Total Products card 0 if empty actual actual std count.
- **TR-R17.2**: "Welcome," full_name not "User" string).
- **TR-R17.3**: Non-admin → /admin route attempt → route blocked).

---

## Task 18: Compliance Passport (FR-8, FR-9)

**Priority**: high  **Status**: pending  **AC**: F4, F6, FR-8, FR-9, AC-R4, AC-R6, AC-R11, T4-T6

### Scope
- Empty state product list if none).
- Add Product modal all fields product create).
- Match standards button calls POST match then GET matches.
- fix score parentheses bug.
- Matched standard expanded requirement checklist fetched. Save per item. summary card with per standard 6 statuses + score.

### Files
- pages/CompliancePassport.tsx update components modals CreateProductModal

### TRs
- **TR-R18.1**: Add product → appears sidebar.
- **TR-R18.2**: Match button → matches list populate scores correct formula (match_score || 0) * 100.
- **TR-R18.3**: expanded standard → checklist 5+ items NOT_STARTED.
- **TR-R18.4**: Save PASSED items → score updates).

---

## Task 19: Knowledge Search UI (Citations + Insufficient text, exact sentence)

**Priority**: high  **Status**: pending  **AC**: F11, FR-11, FR-17, FR-18, T1, T2, T3, T8, T9

### Scope
- sources card renders all citation fields  collapsible source_authority pill badge.
- insufficient evidence → show exact insufficient sentences verbatim panel).
- exact IS click link /standards/:id.
- chat conversation history list.

### Files
- pages/KnowledgeSearch.tsx

### TRs
- **TR-R19.1**: curd query → shows exact insufficient sentences (T1) either).
- **TR-R19.2**: exact IS 17342 → standard_number shows top result; top sources card includes standard_number/clause/page number.
- **TR-R19.3**: answer chunks only context-derived chunks only not mock prefix.

---

## Task 20: StandardsList.tsx + StandardDetailPage.tsx

**Priority**: high  **Status**: pending  **AC**: F3, F5, FR-2, T2, T3

### Scope
- /standards list, category filters pagination; standards/:id tabs overview clauses requirements tests related standards.
- Breadcrumb back; link from Search, from matched cards T2 T3).

### Files
- New pages/StandardsList.tsx; pages/StandardDetailPage.tsx; App.tsx routes.

### TRs
- **TR-R20.1**: /standards lists ≥ 7 cards.
- **TR-R20.2**: IS17342 detail page clauses tab ≥ 5 clauses.
- **TR-R20.3**: Click Compliance match card standards number → navigates detail page).

---

## Task 21: DocumentAnalysis no setTimeout → Real Uploads FR-10, FR-18

**Priority**: medium  **Status**: pending  **AC**: F7, AC-R7, FR-18, AC-R11, T7

### Scope
- remove setTimeout mock → real POST FormData upload;
- loading spinner, error retry.
- render standards, entities, evidence/missing, disclaimer always rendered).
- compliance_score != 85 always fixed bug gone).

### Files
- pages/DocumentAnalysis.tsx

### TRs
- **TR-R21.1**: grep setTimeout DocumentAnalysis.tsx → 0 hits.
- **TR-R21.2**: Analyze txt IS17342; clause 4.2 → shows.

---

## Task 22: LabMatcher API only no mockLabs mailto, FR-12 badges AC-R8, AC-R11, T10

**Priority**: medium  **Status**: pending  **AC**: F8, AC-R8, T10

### Scope
- Remove mockLabs.
- fetch GET /laboratories filter.
- fix mojibake email icon Mail icon lucide.
- Contact Lab mailto.
- Empty state exact exact required sentence card;
- DEMO badge pill on cards;

### Files
- pages/LabMatcher.tsx

### TRs
- **TR-R22.1**: grep mockLabs LabMatcher.tsx → zero hits.
- **TR-R22.2**: search city=NABL → filter works from DB.
- **TR-R22.3**: Email display icon Mail, contact Lab mailto works).
- **TR-R22.4**: Empty state shows exact exact T10 required sentence.

---

## Task 23: KnowledgeGraph.tsx mockGraph removed realGraph + zoom refresh FR-14, FR-18, AC-R9

**Priority**: medium  **Status**: pending  **AC**: F9, AC-R9

### Scope
- remove mockGraph object. Use API /graph/data.
- edges render lines or simple SVG node grid + edge list + svg lines (if feasible). edges actually rendered lines.
- Zoom CSS transform scale on button click).
- Refresh refetch data → refresh button works.
- View Details → navigate appropriate page types standard node.
- Statistics matches API counts.

### Files
- pages/KnowledgeGraph.tsx

### TRs
- **TR-R23.1**: grep mockGraph → zero hits.
- **TR-R23.2**: nodes + edges counts API call data stats matches API count.
- **TR-R23.3**: click standard node → scope/category in side panel).
- **TR-R23.4**: zoom button scale style applied).
- **TR-R23.5**: refresh → re-fetches network.

---

## Task 24: Minor UX polish Admin page + colors/icons consistent + spinner + toast +

**Priority**: low  **Status**: pending  **AC**: F14, AC-Ru1, FR-18

### Scope
- AdminPage users tabbed; role update role patch save.
- Tailwind primary colors to pages inconsistency fixes.
- components/Spinner component submit all async.
- toast container singleton error api events.
- LoadProducts compliance etc.

### Files
- pages/AdminPage.tsx new. App.tsx add route.
- components/Spinner.tsx, ToastContainer.tsx.
- All pages: replace bg-blue-600 classes → primary.

### TRs
- **TR-R24.1**: Non-admin blocked AdminPage 403 card).
- **TR-R24.2**: Change role  MSME → saves persist DB AC-R20.2.

---

## Phase 7 — Final Verification

## Task 25: Scenario Test Suite 1-10 Manual Run (T1-T10, Demo Flow Final

**Priority**: high  **Status**: pending  **AC**: All ACs

### Scope
- verify every scenario documented in spec.md AC-T1 … AC-T10 T10 scenarios.
- Document pass evidence output logs, screenshots.
- Fix any remaining ad-hoc failures found during verify.
- run pytest suite.

### Files
- `docs/DEMO_FLOW.md step by step instructions) optional internal.

### TRs
- **TR-R25.1 (rule)**: T1 "curd" query → sources[].sim ≥ 0.45. Required exact no sentence.
- **TR-R25.2 (rule)**: T2 exact IS returns correct standard top.
- **TR-R25.3 (rule)**: T3 product match ≥1 score ≥0.55).
- **TR-R25.4 (rule)**: T4 create product → appears in list.
- **TR-R25.5 (rule)**: T5 load products → returns correct empty state works.
- **TR-R25.6 (rule)**: T6 select product loads matches + compliance summary checklist shows NOT_STARTED with "Not Yet Assessed".
- **TR-R25.7 (rule)**: T7 upload doc analyse doc → stores analysed.
- **TR-R25.8 (rule)**: T8 Cert → evidence-backed, demo applicability NOT compulsory demo.
- **TR-R25.9 (rule)**: T9 unknown question → exact insufficient sentence.
- **TR-R25.10 (rule)**: T10 lab search → DB labs mockLabs removed)
- **TR-R25.11 rubric 0-2 Manual Demo flow 23 steps walkthrough; score rubric ≥ 1.

---

## Dependency Order

| Phase | Tasks Order |
|---|---|
| Foundation | 1 → 2 |
| Backend APIs | 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12 → 13 |
| Eval + Tests | 14 → 15 |
| Frontend wiring | 16 → 17 → 18 → 19 → 20 → 21 → 22 → 23 → 24 |
| Verify & Delivery | 25 |
