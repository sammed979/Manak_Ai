# MANAK AI Fix & Complete — Product Requirements Document (v2)

## Overview
- **Summary**: Fix & complete the existing MANAK AI prototype (BIS Problem Statement 26107) into a reliable, evidence-first BIS knowledge and compliance assistant, using the existing React/TypeScript/Vite frontend, FastAPI/SQLAlchemy backend, SQLite/Postgres database, and RAG architecture wherever possible.
- **Purpose**: Eliminate hard-coded demos, fake scores, mock timeouts, disconnected buttons, weak search results, and hallucinated answers; make every page and every functional button work end-to-end against real data and real services.
- **Target Users**: CONSUMER / STUDENT / MANUFACTURER / MSME / LABORATORY / COMPLIANCE_OFFICER / ADMIN.

---

## 0. Audit Findings & Feature-to-Code Map (Section 1 Completed)

### 0.1 Verified Database State (2026-09-24)
| Table | Count | Status |
|---|---|---|
| standards | 4 | Seeded (IS 17342, IS 302-1, IS 6911, IS 1573) |
| standard_clauses | 0 | **EMPTY — blocking compliance & clause search** |
| requirements | 0 | **EMPTY — blocking compliance passport** |
| tests / test_methods | 0 / 0 | **EMPTY** |
| certification_schemes | 0 | **EMPTY** |
| laboratories | 0 | **EMPTY — LabMatcher falls back to mock array** |
| hallmarking_centres | 0 | **EMPTY** |
| products | 0 | **EMPTY — "Load Products" button returns [] with no empty state** |
| product_standard_matches | 0 | **EMPTY** |
| knowledge_documents / knowledge_chunks | 6 / 7 | Only 6 docs, 7 chunks, no structured metadata |
| faqs / circulars | 0 / 0 | **EMPTY** |
| users | 1 | admin@manak.ai only |
| organizations | 0 | **EMPTY** |
| compliance_checks / items | 0 / 0 | **EMPTY** |
| conversations / messages | 0 / 0 | **EMPTY** |
| admin_audit_logs | 0 | **EMPTY** |

### 0.2 Verified Broken-Feature Evidence
1. **Search "curd"** (2026-09-24) → Top-1 result = **"stainless steel water bottle (IS 17342:2020)"**, similarity=0.3099 (**31%**), combined_score=0.217 → **weak match NOT rejected**. LLM answer is hardcoded `"This is a mock response for: Context information..."`.
2. **Search "IS 17342:2020 water bottle stainless steel"** → Top-1 is a **BIS overview chunk**, not the IS 17342 standard chunk — keyword search fails to prioritize exact IS-number match. Similarity only 0.56 and still confidence=INSUFFICIENT_EVIDENCE with answer still being a mock.
3. **Compliance Passport "Load Products"** → `GET /products/` returns 401 when no token (no route guard); when authenticated, returns 0 records with **no empty-state card**, button just re-runs the same list → no visible feedback, user thinks button is broken. `POST /products` has no frontend form, so products can't be created in UI.
4. **Document Analysis** → `handleAnalyze()` is a `setTimeout(…, 2000)` with fixed `complianceScore: 85` and hard-coded standards/issues/recommendations. No `POST /document/analyze` backend endpoint.
5. **Lab Matcher** → Uses `mockLabs` array (3 hardcoded labs). State `labs` starts empty, so on first render `labs.length>0 ? labs : mockLabs` shows mockLabs but never actually calls API. Email icon is mojibake `ðŸ“§`. "Contact Lab" button has no onClick.
6. **Knowledge Graph** → Uses `mockGraph` 8 nodes + 9 edges static object. Zoom/Refresh/View Details buttons have NO onClick handlers. Edges never rendered as lines.
7. **Dashboard** → `Total Products: 0` / `Standards Found: 0` / `Compliance Score: 0%` hard-coded in JSX. `Welcome, User` hard-coded. No call to `/auth/me` or `/dashboard/stats`.
8. **Knowledge Search** → UI displays answer but doesn't show the exact required sentence on INSUFFICIENT_EVIDENCE. Answer is always the `MockLLMService` hard-coded prefix. No query understanding. No exact-IS-number boost.
9. **CompliancePassport bugs** → (a) score math `(match.match_score || 0 * 100)` evaluates `0 * 100` first → display bug. (b) "Match Standards" button line 138 calls `loadMatches()` (GET existing) — never calls `POST /products/:id/match-standards`. (c) No requirement checklist; only 3 fields per match.
10. **No route guards** → `/dashboard`, `/compliance-passport`, `/document-analysis`, `/lab-matcher`, `/knowledge-graph`, `/knowledge` all accessible without token → all API calls 401 → all UIs silently empty.
11. **Auth refresh token discarded** → `LoginPage.tsx` line 23: `apiClient.setToken(response.data.access_token)` — `refresh_token` field from backend response thrown away.
12. **No Standards listing / StandardDetail routes** → Cannot view clauses/requirements/schemes despite 4 seeded standards. No `/standards` page, no `/standards/:id` page.
13. **RAG confidence INSUFFICIENT but chunks still sent to LLM** → For "curd" 31% match still appears in context and still gets rendered as a source. Weak evidence NOT filtered.
14. **Knowledge chunks lack structured metadata** → metadata JSON has only 4-5 fields each, missing: `product_category, product_keywords, clause_number, clause_title, standard_status, version, effective_date, source_url, source_authority, page_number, last_verified`.
15. **Knowledge NOT separated by type** → Standard clauses, test methods, certification schemes, QCOs, labs, FAQs, circulars, product manuals — all generic text in `KnowledgeChunk`; no typed separate retrieval per `DocumentType`.
16. **Authoritative source tier missing** → `AuthorityLevel` enum exists but no records use it consistently; UI never displays DEMO badge for demo data.
17. **Certification applicability hardcoded as YES/NO** → `ProductStandardMatch.is_mandatory` is just a string; never derived from QCO/scheme evidence.
18. **Multilingual not wired** → `TRANSLATION_PROVIDER` in settings, no translation layer, no language selector UI, no `lang` param passed to any endpoint.
19. **Knowledge Graph not from DB relationships** → Static 8-node mock. No edges from `StandardClause.standard_id`, `Requirement.clause_id`, etc.
20. **Conversations, Citations, Admin, Audit** → Tables exist. No endpoints. No evaluation dataset. No pytest suite.

### 0.3 Feature → Frontend → API → Service → DB → AI/DataSource
| Feature | Frontend Component | API Endpoint(s) | Service/Engine | DB Model(s) | AI/Source |
|---|---|---|---|---|---|
| Auth Login/Register | [LoginPage](file:///c:/TURBOC3/Projects/Manak%20Ai/frontend/src/pages/LoginPage.tsx), [RegisterPage](file:///c:/TURBOC3/Projects/Manak%20Ai/frontend/src/pages/RegisterPage.tsx) | `POST /auth/login`, `/register`, `/refresh`, `/me` | [auth.py](file:///c:/TURBOC3/Projects/Manak%20Ai/backend/app/security/auth.py), [dependencies.py](file:///c:/TURBOC3/Projects/Manak%20Ai/backend/app/security/dependencies.py) | User, Organization | JWT (HS256) + bcrypt |
| Dashboard Stats | [DashboardPage](file:///c:/TURBOC3/Projects/Manak%20Ai/frontend/src/pages/DashboardPage.tsx) | **MISSING** `/dashboard/stats` | **MISSING** | aggregates (products, standards, …) | — |
| Standards Search/List | **MISSING** StandardsList.tsx | **MISSING** `GET /standards`, `/standards/:id` | **MISSING** | Standard, StandardClause, Requirement, Test | — |
| AI Knowledge Search | [KnowledgeSearch](file:///c:/TURBOC3/Projects/Manak%20Ai/frontend/src/pages/KnowledgeSearch.tsx) | `POST /knowledge/search` (works) | [rag/engine.py](file:///c:/TURBOC3/Projects/Manak%20Ai/backend/app/rag/engine.py), [retriever.py](file:///c:/TURBOC3/Projects/Manak%20Ai/backend/app/rag/retriever.py) | KnowledgeDocument, KnowledgeChunk | [ai/llm.py](file:///c:/TURBOC3/Projects/Manak%20Ai/backend/app/ai/llm.py) (Mock only), [ai/embeddings.py](file:///c:/TURBOC3/Projects/Manak%20Ai/backend/app/ai/embeddings.py) (MD5 mock) |
| Knowledge Ingest | API only | `POST /knowledge/ingest` | [knowledge/ingestion.py](file:///c:/TURBOC3/Projects/Manak%20Ai/backend/app/knowledge/ingestion.py) | KnowledgeDocument, KnowledgeChunk | MockEmbeddingService |
| Product CRUD | API only, **no create form** in UI | `POST /products`, `GET /products`, `GET /products/:id` | — | Product | — |
| Product→Standard Match | [CompliancePassport](file:///c:/TURBOC3/Projects/Manak%20Ai/frontend/src/pages/CompliancePassport.tsx) | `POST /products/:id/match-standards`, `GET /products/:id/matches` | [product/matching.py](file:///c:/TURBOC3/Projects/Manak%20Ai/backend/app/product/matching.py) | ProductStandardMatch, Standard | MockEmbedding cosine |
| Compliance Check Items | CompliancePassport **MISSING checklist view** | **MISSING** `GET /products/:id/compliance/:standard_id/items`, `PATCH /compliance/items/:item_id`, `GET /products/:id/compliance/summary` | [product/compliance.py](file:///c:/TURBOC3/Projects/Manak%20Ai/backend/app/product/compliance.py) | ComplianceCheck, ComplianceCheckItem, Requirement | — |
| Document Analysis | [DocumentAnalysis](file:///c:/TURBOC3/Projects/Manak%20Ai/frontend/src/pages/DocumentAnalysis.tsx) (setTimeout fake) | **MISSING** `POST /documents/analyze` | **MISSING** document extractor/analyzer | (KnowledgeDocument / new uploads) | — |
| Lab Matcher | [LabMatcher](file:///c:/TURBOC3/Projects/Manak%20Ai/frontend/src/pages/LabMatcher.tsx) (mockLabs) | **MISSING** `GET /laboratories`, `GET /hallmarking/centres` | **MISSING** | Laboratory, HallmarkingCentre | — |
| Knowledge Graph | [KnowledgeGraph](file:///c:/TURBOC3/Projects/Manak%20Ai/frontend/src/pages/KnowledgeGraph.tsx) (mockGraph) | **MISSING** `GET /graph/data`, `/graph/node/:id` | **MISSING** graph builder | Standard↔Clause↔Requirement↔Test↔Laboratory, Standard↔Scheme | — |
| Multilingual | **MISSING** LanguageSelector | **MISSING** `lang` param in RAG | **MISSING** translation layer | — | MockTranslator TBD |
| Chat History | API only, **MISSING** sessions UI | **MISSING** `/chat/sessions`, `/chat/sessions/:id/messages` | RAGEngine | Conversation, ConversationMessage | LLM |
| Admin Panel | **MISSING** AdminPage | **MISSING** `/admin/users`, `/admin/analytics`, `/admin/audit-logs`, `/admin/knowledge/reindex` | **MISSING** audit hooks | AdminAuditLog | — |

---

## Goals

1. Fix the 20 verified audit issues WITHOUT rebuilding the app. Preserve existing pages, routes, layout, colors, branding, file structure, folder names, and naming conventions.
2. Make "Knowledge Base Search" accurate via structured metadata, a full hybrid search pipeline, query understanding, and relevance thresholds that **reject 31% weak matches like "curd → stainless steel water bottle"**.
3. Make every button on every page work: **Load Products, Match Standards, Analyze Document, Lab Search, Zoom/Refresh Graph, View Details, Contact Lab, Search**.
4. Make every response evidence-first. No hallucinated standards, clauses, labs, QCOs, URLs. Show citations (source, IS number, clause, page, URL, version, last verified).
5. Make Compliance Passport fully functional: create products, load existing products, match standards, open per-standard requirement checklist with 6 statuses, compute score from actual requirement states.
6. Seed DEMO-labeled data for all empty tables (clauses, requirements, tests, schemes, labs, hallmarks, products, docs, FAQs, circulars).
7. Implement 10 exact final-test scenarios end-to-end.
8. Add evaluation dataset (queries/expected) + pytest test suite.

## Non-Goals

- Do NOT swap React/FastAPI/SQLite+Postgres stack. Do NOT add Next.js, Django, or Mongo.
- Do NOT redesign the UI. Do NOT change route paths. Keep `/dashboard`, `/knowledge`, `/compliance-passport`, `/document-analysis`, `/lab-matcher`, `/knowledge-graph`, `/login`, `/register`, `/`.
- Do NOT invent official BIS data. Every seeded record MUST be clearly labeled DEMO; no misrepresentation.
- Do NOT require LLM/embedding API keys for the app to run. If no keys: "improved mock" must use retrieved context chunks directly (no hardcoded mock prefix strings).
- Do NOT add new database: SQLite local + Postgres in Docker, both remain supported.

---

## Section 2: Functional Requirements — Structured Knowledge Data

### FR-2 (Metadata Schema for Knowledge)
- Every knowledge record (ingested via `POST /knowledge/ingest` and in seed scripts) MUST contain structured metadata with **ALL** of: `standard_number, title, product_category, product_keywords, scope, clause_number, clause_title, content, document_type, standard_status, version, effective_date, source_url, source_authority, page_number, last_verified`. Missing values MUST be stored as `null`/empty, never omitted.
- The app MUST support and separately store these **11 typed document categories**, either as separate tables or as explicit `document_type` enum with typed metadata: `STANDARD, CLAUSE, REQUIREMENT, TEST, CERTIFICATION_SCHEME, QCO, LABORATORY, FAQ, CIRCULAR, PRODUCT_MANUAL, OTHER`. Do NOT store everything as generic text in a single `content` field without a type.
- `DocumentType` enum in code MUST reflect the 11 categories above, mapped to the existing `AuthorityLevel` enum.

## Section 3: Functional Requirements — Hybrid Search Pipeline

### FR-3 (Full Hybrid Pipeline)
Every `POST /knowledge/search` request MUST execute this pipeline, in order, with each stage observable via response metadata (`pipeline_steps[]` for ADMIN / DEBUG):
1. **Query Cleaning** — strip extra whitespace, trim, remove control characters, lowercase for keywords.
2. **Intent Detection** (Section 6) — classify into 12 intent classes.
3. **Entity / Product Extraction** (Section 5) — extract Product, Category, Industry, Intent, Keywords, Synonyms, IS number (regex `IS\s?\d+(:\d+)?(-\d+)?`), Location if present.
4. **Lexical (Keyword/BM25) Search** — keyword substring match + TF-weighted scoring over content, title, standard_number, metadata. Exact IS-number substring match receives a **+2.0 boost** (100x priority over any other token).
5. **Semantic (Vector) Search** — cosine similarity over `KnowledgeChunk.embedding` (current pickle embeddings; keep for SQLite).
6. **Metadata Filtering** — filter candidates by extracted `product_category`, `standard_number`, `clause_number`, `document_type`, `intended_industry`. If intent is LABORATORY, route ONLY to Laboratory table. If intent is HALLMARKING, route ONLY to HallmarkingCentre table.
7. **Candidate Retrieval** — top-K=20 lexical + top-K=20 semantic, union by document_id.
8. **Cross-Encoder Reranking** (deterministic fallback without external model): rerank candidates on weighted score: `score = 0.35*lexical + 0.45*semantic + 0.20*metadata_match_score + exact_IS_match_bonus(0 or 2)`. If external reranker model configured, use it; otherwise keep deterministic formula above.
9. **Relevance Threshold** (Section 4) — drop candidates below configurable `MIN_RELEVANCE_SCORE` / `MIN_SEMANTIC_SIMILARITY`. If final candidate list is empty, go straight to no-evidence response WITHOUT calling LLM.
10. **Evidence Validation** — ensure each candidate has at least `document_title, source_authority`; discard malformed entries.
11. **LLM Answer Generation** (Section 17) — feed ONLY the top `final_candidates` (after all previous filters) into the LLM prompt.

## Section 4: Functional Requirements — Relevance Threshold & No-Answer

### FR-4 (Configurable Thresholds)
- Introduce these tunable thresholds in `settings.py` (overridable via env):
  - `MIN_SEMANTIC_SIMILARITY` = **0.45** (default): drop chunks below this raw cosine.
  - `MIN_FINAL_SCORE` = **0.50** (default): drop below reranked final score.
  - `MIN_EVIDENCE_CHUNKS` = **1** (default): need at least this many passing candidates.
  - `MAX_LLM_CONTEXT_CHUNKS` = **5** (default): cap what's fed to LLM.
- Example hard rejection: query "curd" vs 0.3099 similarity to "stainless steel water bottle" → 0.3099 < 0.45 → **chunk removed, not returned, not sent to LLM**. If 0 candidates remain after filtering → do not call LLM → return:
  ```json
  {
    "answer": "No sufficiently relevant authoritative information was found for this query in the current knowledge base.",
    "sources": [],
    "confidence": "INSUFFICIENT_EVIDENCE",
    "context_used": 0,
    "rejected_as_irrelevant": true
  }
  ```
- Additionally: when `confidence == INSUFFICIENT_EVIDENCE` for any other reason (ambiguous, no docs match type, etc.), the `answer` field MUST say exactly: *"I could not find sufficient authoritative evidence to answer this confidently."*
- Do NOT send weak-chunk evidence into the LLM prompt. Rejection MUST happen BEFORE prompt construction.

## Section 5: Functional Requirements — Query Understanding

### FR-5 (Structured Query Parse)
Create `QueryUnderstanding` service that returns a typed dict from user text:
```python
{
  "raw": str,
  "cleaned": str,
  "intent": IntentEnum (12 values),
  "product": Optional[str],  # e.g. "stainless steel water bottle"
  "category": Optional[str],  # from ProductCategory enum or UNKNOWN
  "industry": Optional[str],
  "keywords": list[str],  # cleaned keyword set
  "synonyms": dict[str, list[str]],  # "bottle" → ["container", "flask", …]
  "is_numbers": list[str],  # regex matches, e.g. ["IS 17342:2020"]
  "clause_numbers": list[str],  # e.g. ["4.2"]
  "location": Optional[dict[str, str]],  # {city, state, country}
  "certification_needed": Optional[bool],
  "testing_needed": Optional[bool]
}
```
- Extraction rules: IS number regex `r'\bIS\s*(\d+(?:[:\-\w]*\d+)?)'` (case-insensitive). Clause regex `r'\b(?:clause|cl)\.?\s*(\d+(?:\.\d+)*)'`.
- Product category mapping: map noun-phrases into the existing `ProductCategory` enum.
- Example: *"Which BIS standard applies to stainless steel water bottle?"* → intent=STANDARD_SEARCH, product="stainless steel water bottle", category=CONSUMER_PRODUCTS (from existing enum), keywords=["stainless steel","bottle","drinking water","water bottle"], is_numbers=[], synonyms={"stainless steel":["SS","food grade steel"]}, testing_needed=None.

## Section 6: Functional Requirements — Intent Routing (12 Intents)

### FR-6 (Intent Enum & Routing)
- Create `Intent` enum with exactly 12 values:
  `STANDARD_SEARCH, PRODUCT_STANDARD, CERTIFICATION, TESTING, LABORATORY, HALLMARKING, DOCUMENT_ANALYSIS, COMPLIANCE, CLAUSE_QUERY, STANDARD_COMPARISON, RELATED_STANDARD, GENERAL_BIS, UNKNOWN`.
- Add intent router in `RAGEngine.search()`:
  - `LABORATORY` → route to `GET /laboratories` filtered by keywords + location (return result as evidence chunks).
  - `HALLMARKING` → route to HallmarkingCentre table.
  - `CERTIFICATION` → prioritize CertificationScheme + QCO documents.
  - `CLAUSE_QUERY` → route to StandardClause + Requirement tables, filtered by clause_number.
  - `STANDARD_SEARCH` / `PRODUCT_STANDARD` → hybrid search over Standard + CLAUSE + REQUIREMENT + TEST documents.
  - `UNKNOWN` → run hybrid search over all documents, lower default confidence.
- Intent classifier: if exact IS regex matched → forced `STANDARD_SEARCH`. If "hallmark" in text → forced `HALLMARKING`. If "lab" or "laboratory" or "accredited" + test → `LABORATORY`. Else keyword fallback → deterministic classifier. Optional: if OpenAI key present, classify via LLM prompt; always fallback to deterministic classifier so no-keys scenario works.

## Section 7: Functional Requirements — Structured Product Intelligence & Recommendation

### FR-7 (Product Intelligence)
- Extend Product model with structured fields (nullable, backward-compatible) to drive recommendation:
  `subcategory, material (str), intended_use (str), industry (str), technical_attributes (JSONB / JSON text), keywords (str/JSON list)`.
- Product→Standard matching pipeline, replacing/augmenting the 3-strategy matcher in `product/matching.py`:
  1. **Product Classification** → map product.name + category + material + intended_use into keyword vector.
  2. **Candidate Standards** → filter standards by `product_category` (standards table), plus `standards.keywords` overlap.
  3. **Scope Matching** → token overlap + semantic cosine between product description and standard.scope.
  4. **Semantic Matching** → concatenate `product.name + " " + product.description + " " + product.material + " " + product.intended_use` → embed → cosine vs standard-level embedded summary (or chunk embedding mean).
  5. **Metadata Matching** → explicit standard_number / category / industry overlaps computed (0.0–1.0).
  6. **Reranking** → weighted merge: `0.3*scope + 0.3*semantic + 0.25*keyword + 0.15*metadata`.
  7. **Explain Recommendation** — for every match, compute `match_reason` string: `"Scope overlap: 6 keywords (stainless, steel, bottle, drinking, water, food-grade) + semantic similarity 0.71 + material match"`.
- Frontend match card MUST show:
  | Field | Source |
  |---|---|
  | Standard Number | standard.standard_number |
  | Title | standard.title |
  | Scope | standard.scope (truncated with expand) |
  | Why Relevant | match_reason |
  | Evidence | Top-2 overlapping keywords with standard.scope |
  | Confidence | `(match_score * 100).toFixed(1)` % |
- Applicability labels: NEVER claim "Mandatory" unless a QCO / CertificationScheme link record EXISTS with evidence. Otherwise show `"Potentially Relevant"` pill instead of hard YES/NO. `is_mandatory` becomes 4-state enum: `COMPULSORY, VOLUNTARY, NOT_DETERMINED, EVIDENCE_INSUFFICIENT`.

## Section 8: Functional Requirements — Fix "Load Products" & Product APIs

### FR-8 (Product API Fixes & Empty States)
Tracing Load Products flow:
1. Button `onClick={loadProducts}` → calls `apiClient.listProducts()` → `GET /products` → `require_any_role(MANUFACTURER, ADMIN, COMPLIANCE_OFFICER, MSME)` (line in products.py) → if user has no manufacturer org, return all (consumer may still see DEMO products) → return JSON list.
2. If `products.length === 0`, CompliancePassport sidebar MUST render styled empty card: *"No products found. Create your first product."* with CTA → opens the Create Product modal.
3. **Auth guard required**: CompliancePassport + Dashboard + Knowledge + DocumentAnalysis + LabMatcher + KnowledgeGraph routes MUST all be wrapped in `AuthGuard` → `/login` redirect on 401/no token.
4. New frontend modal "Add Product" in CompliancePassport: fields name, description, category, subcategory, brand, sku, model, material, intended_use, target_market, specifications (optional JSON stringified), keywords (comma separated). Submits `POST /products`.
5. Existing route conventions MUST be followed (no path changes):
   - `GET /products` (list, filtered by role)
   - `GET /products/:id` (detail)
   - `GET /products/:id/compliance` → redirect to new `/products/:id/compliance/summary`
   - `POST /products` (create product, authenticated)
   - `POST /products/:id/analyze` (product intelligence analysis: runs match + returns matches + standard list via new endpoint)

## Section 9: Functional Requirements — Compliance Passport with 6 Statuses & Score Logic

### FR-9 (Compliance Passport)
- Per product, when user opens a matched standard card → fetch checklist via `GET /products/:id/compliance/:standard_id/items`. Endpoint auto-creates a `ComplianceCheck` row if none exists, with items per linked `Requirement` (all default PENDING).
- Item fields (rendered per row in expandable standard section):
  - Clause reference (e.g. "Clause 4.2")
  - Requirement description
  - Status dropdown with 6 options: `NOT_STARTED, IN_PROGRESS, PENDING_VERIFICATION, PARTIALLY_SATISFIED, SATISFIED, UNKNOWN`.
  - Evidence (text / URL)
  - Notes
  - Save button (PATCHes `/compliance/items/:item_id`)
- **Score calculation**: computed by backend ONLY from actual saved requirement states:
  - Applicable requirements (all items with status != NOT_APPLICABLE if exists).
  - Score = `(count_SATISFIED + 0.5 * count_PARTIALLY_SATISFIED) / count_applicable_items`.
  - Fraction rendered as `(score * 100).toFixed(1) %`.
  - **No items saved / all NOT_STARTED or UNKNOWN**: score rendered as text `Not Yet Assessed`, numeric score null, not sent to LLM.
- **Rollup status per standard**:
  - All NOT_STARTED/UNKNOWN → NOT_STARTED, CTA "Start Assessment".
  - Any IN_PROGRESS → IN_PROGRESS.
  - Any PARTIALLY_SATISFIED without all SATISFIED → PARTIALLY_SATISFIED.
  - All SATISFIED → SATISFIED.
  - Submitted but no reviewer (admin role) touch → PENDING_VERIFICATION when status notes or evidence all filled but admin not approved.
- UI for the Compliance Passport: Product info header card → Matched Standards tabs/accordion → each standard expanded shows:
  - Summary card (status pill + score + "Not Yet Assessed" text if applicable)
  - Requirements checklist (table with status/evidence/notes/save)
  - Documents linked (uploaded doc analysis)
  - Testing tab (linked tests & laboratories)
  - Certification Guidance card (from CertificationScheme + QCO links)
  - Compliance Gaps card (all items with status != SATISFIED / NOT_APPLICABLE)
  - Sources (all standard/scmeme/lab citations)

## Section 10: Functional Requirements — Document Analysis Pipeline

### FR-10 (Document Analysis)
- New endpoint `POST /api/v1/documents/analyze` accepts:
  `multipart/form-data`: file (required), product_id (optional), standard_id (optional), lang (optional default en).
- New `documents/` module with extractor + analyzer classes. 12-step pipeline, logged in `analysis_meta[]`:
  1. Validate: file size < 15MB; allowlist `.txt, .md, .pdf, .doc, .docx, .png, .jpg, .jpeg, .tiff`. Reject others 400.
  2. Extract text: TXT→read; DOCX→python-docx paragraphs; PDF→PyMuPDF `get_text()` preserving page numbers. Images: Pillow + OCR (pytesseract) if installed; otherwise warning `"OCR unavailable — install tesseract-ocr for image text extraction"`; no text stored.
  3. Identify Document: classifier over keywords/standard refs → guessed `DocumentType`.
  4. Extract Entities: regexes for `IS numbers`, `Clause numbers`, `certificate refs` (CM/LM/MN prefixes), `Lab names`, `manufacturers`, `YYYY-MM-DD / DD/MM/YYYY dates`, `license numbers`.
  5. Match Requirements: if `standard_id` provided → load `Requirement` rows. For each, check if extracted text contains requirement keywords/phrases → build evidence row with `{requirement_id, snippet, page_refs: [], present: bool}`.
  6. Map Evidence: join findings against DB entities.
  7. Identify Gaps: requirements where `present=false`.
  8. Compute match score if standard_id given: `evidence_present / (present+missing)`. Never fixed 85.
  9. Sanitize filename, store UUID-prefixed on disk (`./backend/uploads/`) OR in-memory SpooledTemporaryFile; stored paths recorded in `KnowledgeDocument.source_url="file://..."` if user clicks "Ingest to KB".
  10. Build final response with: `{file_name, file_size, extracted_text_preview, pages_found, standards_found[], entities_found, evidence[], missing[], compliance_score, language, warnings, disclaimer}`.
  11. Always show top-level disclaimer: *"This analysis is informational only — MANAK AI does not certify that this document is legally valid or BIS-compliant."*
  12. Never say "valid", "approved", "compliant guaranteed" merely because AI found text.
- Frontend: remove `setTimeout`, remove fixed `complianceScore: 85`, replace with real FormData upload, spinner loading state, error panel, standards/entities/evidence/missing cards.

## Section 11: Functional Requirements — Citations & Evidence

### FR-11 (Citations)
- Every AI `answer` that contains a factual claim about a standard, requirement, lab, scheme, or testing MUST include `sources[]` with structured citation metadata:
  ```typescript
  interface Citation {
    source: string;  // e.g. "KnowledgeDocument" / "Standard" / "Laboratory"
    document_title: string;
    document_type: string;
    standard_number?: string;
    clause?: string;
    page?: number | null;
    url?: string;
    version?: string;
    last_verified?: string;
    source_authority: "OFFICIAL_BIS" | "OFFICIAL_GOVT" | "VERIFIED_THIRD" | "UNVERIFIED_DEMO";
    chunk_content: string;
    similarity: number;
  }
  ```
- Frontend `KnowledgeSearch` sources card MUST render all the above fields that are non-null; collapsible chunk content; `source_authority` pill (colored: OFFICIAL_BIS green, GOVT blue, DEMO red badge).
- Rule: **Do not create citations that don't exist in the DB**. If a standard number is referenced but not in `standards`/`knowledge_documents`, say "referenced standard not in current knowledge base" rather than fabricating a citation.

## Section 12: Functional Requirements — Authoritative Source Priority

### FR-12 (Source Tiering)
- Extend `AuthorityLevel` enum to 4 tiers exactly (existing enum → update):
  1. `OFFICIAL_BIS` — BIS Act, BIS Standards, Schemes, QCOs, Circulars issued by BIS, BIS labs directory.
  2. `OFFICIAL_GOVT` — Government of India / ministry QCOs, regulations, gazettes.
  3. `VERIFIED_THIRD` — NABL-accredited lab profiles submitted by users with admin verification, industry-validated supporting sources.
  4. `UNVERIFIED_DEMO` — All DEMO-seeded data, placeholder knowledge, user-uploaded unvetted docs.
- Rerank phase adds +1.2 bonus to tier 1, +0.8 tier 2, +0.4 tier 3, no bonus tier 4.
- UI: Every citation pill / standard card / lab card / product match card MUST display the authority level clearly as a colored pill badge. "DEMO data — not official BIS information" banner on every page that displays UNVERIFIED_DEMO records. `UNVERIFIED_DEMO` sources **cannot** drive a "COMPULSORY" certification claim (max VOLUNTARY, default NOT_DETERMINED).

## Section 13: Functional Requirements — Certification Applicability Logic

### FR-13 (Certification NOT Automatic)
- Rules for `ProductStandardMatch.certification_applicability` (renamed from `is_mandatory`):
  - Value = `COMPULSORY` **only** if a linked QCO (Quality Control Order) record OR `CertificationScheme` record explicitly mandates that standard for that product category, AND source_authority ∈ {OFFICIAL_BIS, OFFICIAL_GOVT}. Evidence stored as `applicability_notes: "QCO XYZ dated 2024-05-20 mandates IS 17342 for stainless steel water bottles." + citation links.
  - Value = `VOLUNTARY` if a BIS Product Certification Scheme record covers that standard.
  - Otherwise `NOT_DETERMINED` or `EVIDENCE_INSUFFICIENT`.
  - **Never** return `COMPULSORY` just because text "mandatory" appears in a general FAQ chunk.
- Frontend: pill color per applicability: Compulsory=red, Voluntary=blue, Not Determined=gray, Insufficient=yellow.

## Section 14: Functional Requirements — Knowledge Graph From DB Relationships

### FR-14 (DB-Backed Graph)
- New endpoint `GET /api/v1/graph/data` returns `{nodes[], edges[]}` built ONLY from actual DB relationship keys:
  - Standard nodes from `standards.id` (type: standard)
  - Clause nodes from `standard_clauses.id` (type: clause)
  - Requirement nodes from `requirements.id` (type: requirement)
  - Test nodes from `tests.id` (type: test)
  - CertificationScheme nodes (type: scheme)
  - Laboratory nodes (type: laboratory)
  - Product nodes (if any, type: product)
- Edge list generated from:
  - `StandardClause.standard_id` → standard ↔ clause edge
  - `Requirement.clause_id` (or `.standard_id` fallback) → clause↔requirement edge
  - `Test.standard_id` → standard↔test edge
  - `CertificationScheme.standards` relationship → standard↔scheme
  - `Laboratory.capabilities` JSON overlaps with test.category → test↔laboratory edge
  - `ProductStandardMatch.product_id / standard_id` → product↔standard edge
- Capped at 500 nodes / 1500 edges to keep renderable. `GET /graph/node/:id` returns full entity. Zoom buttons: CSS transform. Refresh: re-fetch `/graph/data`. View Details: navigate to `/standards/:id` or `/laboratories/:id` or `/products/:id` depending on type.

## Section 15: Functional Requirements — Multilingual EN/HI/KN

### FR-15 (Multilingual Support)
- Settings `TRANSLATION_PROVIDER` (mock default) + new `SUPPORTED_LANGS = ["en", "hi", "kn"]`.
- Translation layer `ai/translation.py` with abstract `Translator` + `MockTranslator` (dictionary-based for 30+ nav strings + canned answer translation map; preserves tech tokens) + `GoogleTranslator` stub (no key needed for mock).
- Token-preserving translation pipeline: Before translate, extract tokens using regexes:
  `(IS\s[\d\-:]+, Clause\s?[\d\.]+, [CM][\d]{5,}, Certificate\s?[A-Z]{0,4}[\d]+, Lab\s?#\d+, http[s]?://\S+)` → replace with `⟪IDX⟫` placeholders → translate → restore placeholders. Guarantees IS / clause / certificate numbers are NEVER translated.
- RAG pipeline: if `lang != en`, translate query to English for retrieval (to match English-seeded corpus) → retrieve → translate answer to requested lang (preserving tokens). If translator fails, set `lang_fallback=true` in response and return English answer.
- Frontend language selector component (in LandingPage nav + Dashboard sidebar). Options: `English (en)`, `हिन्दी (hi)`, `ಕನ್ನಡ (kn)`. Stores choice in localStorage. Appends `lang` to all search/compliance/doc-analyze API calls. Nav strings (Login/Register/Dashboard/etc.) translated via dictionary; untranslated strings fall back to English.

## Section 16: Functional Requirements — Evaluation Dataset

### FR-16 (Eval Dataset)
- Create new file `backend/evaluation_dataset.json` with 40+ rows. Each row:
  ```json
  {
    "query": string,
    "intent": IntentEnum,
    "product": string | null,
    "expected_category": ProductCategoryEnum | null,
    "expected_standard": string | null,  // standard_number e.g. "IS 17342:2020"
    "expected_source_authority": AuthorityLevel | null,
    "expected_clause": string | null,
    "should_answer": boolean,  // true if answer should exist; false if should answer insufficient
    "difficulty": "easy" | "medium" | "hard"
  }
  ```
- Coverage: 10 normal questions, 5 ambiguous, 5 irrelevant (should answer = NO), 5 unknown products, 5 exact IS-number searches, 5 certification, 5 testing/laboratory.
- Add evaluation script `backend/eval_retrieval.py` running the retrieval pipeline (not LLM) against the dataset and outputting:
  | Metric | Definition | Target |
  |---|---|---|
  | Top-1 retrieval accuracy | expected_standard == result[0] | ≥ 80% easy, ≥ 60% overall |
  | Top-5 retrieval accuracy | expected_standard in results[:5] | ≥ 92% easy, ≥ 80% overall |
  | Citation accuracy | expected_clause present in returned citation.clause list, if non-null | ≥ 70% |
  | No-answer accuracy | 1 - false_positive_rate for should_answer=false | ≥ 90% (no answer for "curd" etc.) |
  | Answer groundedness | For subset of 10 where should_answer true, LLM answer words mostly present in returned chunks | ≥ 80% token overlap |
- Target thresholds above are minimums required. Lower = rerun tuning of MIN_SEMANTIC_SIMILARITY / weights / keyword boost until targets pass for seeded dataset.

## Section 17: Functional Requirements — No-Hallucination Policy

### FR-17 (LLM Prompt & Fallback)
- System prompt prefix prepended to EVERY LLM call (including chat, document summaries):
  > *"You are MANAK AI, a precise assistant for Indian Standards (BIS) questions. Use ONLY validated retrieved evidence provided in this prompt to answer. Never invent or assume any standard number, clause number, laboratory, certification scheme, QCO, URL, requirement, or circular. If evidence doesn't exist, reply exactly: 'I could not find sufficient authoritative evidence to answer this confidently.' Cite sources inline. Preserve IS numbers, clause numbers, and certificate identifiers exactly as written."*
- LLM service flow:
  1. If `LLM_PROVIDER=openai` AND `OPENAI_API_KEY` valid → call `gpt-4o-mini` (or configured model) via SDK with the prompt + context chunks.
  2. Else or on failure → `ImprovedMockLLMService.generate()` builds a deterministic structured answer directly from the chunks (no LLM API call):
     - No chunks → return the exact insufficient-evidence sentence.
     - Chunks → answer = "Based on X retrieved source(s):\n" + for each chunk: "[Source i] <first 3 sentences of chunk content>\n" + confidence from engine. Deterministic — never random.
  3. If OpenAI response contains any substring IS number not present in the provided chunk context, regex-scan and replace the hallucinated IS reference with *"[unreferenced number — cite from knowledge]"*. No hallucinated IS → response returned as-is.
- `RAGEngine._calculate_confidence()` stays; add explicit rule: if all candidates ranked below threshold → INSUFFICIENT_EVIDENCE without calling LLM.

## Section 18: Functional Requirements — Frontend UX Fixes

### FR-18 (All Buttons Functional)
Every visible button on every page MUST perform its documented function:
| Page | Button/Control | Action Required |
|---|---|---|
| CompliancePassport | Load Products | `listProducts()` + empty-state card if 0 |
| CompliancePassport | Add Product (new) | Open modal → `POST /products` → refresh list |
| CompliancePassport | Product row click | loadMatches + loadComplianceSummary |
| CompliancePassport | Match Standards | `POST /products/:id/match-standards` → THEN `loadMatches()` |
| CompliancePassport | Match card click | expand checklist via new endpoint |
| CompliancePassport | Save (per requirement) | `PATCH /compliance/items/:item_id` → refresh score |
| KnowledgeSearch | Search | `POST /knowledge/search` + loading spinner + error panel + exact "No sufficiently relevant…" sentence verbatim when rejection |
| DocumentAnalysis | Select File | opens file picker (already works) |
| DocumentAnalysis | Analyze Document | real `POST /documents/analyze` (FormData), remove setTimeout |
| LabMatcher | Search | `GET /laboratories?filters…` → render from response. Remove mockLabs. |
| LabMatcher | Contact Lab | `mailto:lab.email` open default mail client |
| KnowledgeGraph | Zoom In/Out | CSS transform on graph container |
| KnowledgeGraph | Refresh | re-fetch `/graph/data` |
| KnowledgeGraph | Node click | `GET /graph/node/:id` → side panel populate |
| KnowledgeGraph | View Details | navigate to appropriate entity page |
| Dashboard | All 4 quick-action tiles | navigate to the correct page (already uses Link) |
| All pages | Back arrow `<ArrowLeft>` with text "Dashboard" | Navigate to `/dashboard` |
| Language selector (new) | EN/HI/KN click | set UI lang + pass lang to all APIs |

Loading states: replace text "Signing in..." / "Analyzing..." with a `<Spinner />` component. Error states: styled alert cards + retry CTA buttons. Empty states: styled cards + primary CTA to create/add.

## Section 19: Functional Requirements — API Debugging & Error Handling

### FR-19 (API Correctness)
- Fix all classes of errors across the stack:
  - **401s**: Add `AuthGuard` so that unauthenticated users never hit a 401-driven empty page — redirected to login first.
  - **403s**: Admin routes return 403. Frontend shows styled "You don't have permission" card, no blank screen.
  - **404s**: `GET /standards/:id` for non-existent IDs → 404 `{"detail":"Standard not found"}` + frontend 404 card.
  - **422s**: Frontend forms validate fields client-side BEFORE submission using zod (react-hook-form already uses zod patterns or use those already present; ensure zod errors show under inputs).
  - **500s**: Backend catch-all middleware MUST NOT leak Python stack traces. Return `{"detail":"A server error occurred. Please try again."}`. Server-side `logging.exception(e)` records the traceback.
  - **CORS**: Fix `CORS_ORIGINS` env-var parsing (comma→list). Default origins = `["http://localhost:5173", "http://localhost:4173"]`.
  - **Authentication**: bcrypt verified; JWT access token 30 min expiry; refresh token 7 days. Refresh endpoint usable without full re-login.
  - **Timeouts**: Any request > 30s → backend returns 504 `{"detail":"Operation timed out"}` + log. Frontend shows timeout card with retry.
  - **Serialization**: All response schemas use `from_attributes = True`; UUID serialized to string, not UUID object; dates ISO-8601; enums as value strings.
  - **Environment variables**: `.env.example` updated with ALL new settings; backend `settings.py` fails loudly on `DEBUG=False` default JWT secrets detected (production mode).
  - **Database**: `USE_DOCKER_DB` env var correctly parsed; SQLite DB auto-created on first run. Alembic scaffold present (no migrations required, but must not error).
  - **API consistency**: All success = 2xx with typed schema; all client errors = 4xx with `{"detail": string}`; server errors = 5xx with `{"detail": string}`.

## Section 20: Final Test Scenarios (rule acceptance criteria — Section 20 in user request)

See "Acceptance Criteria" AC-T1…AC-T10 for the exact 10 scenarios that must pass.

---

## Non-Functional Requirements

- **NFR-1 (Preservation)**: All 9 existing frontend pages keep current route paths, title text, layout grid structure, primary color palette, and existing lucide-react icon usage. Only bug fixes, new sub-components (modals/checklists/cards), new page routes (`/standards`, `/standards/:id`, `/admin`) added. Additions only. No visual redesign.
- **NFR-2 (Offline operability)**: Fully functional without LLM/embedding/translation/OCR keys using improved mock providers; answer text derived deterministically from chunk content.
- **NFR-3 (Performance)**: List endpoints paginated with default limit 50, max limit 200. Graph endpoint capped as specified. No unbounded queries.
- **NFR-4 (Testability)**: A pytest suite in `backend/tests/` covers auth, standards, graph, products, RAG, documents, labs with TR pass/fail.
- **NFR-5 (Security)**: All uploads sanitized; filename traversal stripped; executable `.exe/.bat/.sh/.ps1` uploads rejected; no raw SQL used; bcrypt cost factor ≥ 12; no hardcoded secrets in any committed file; DEBUG=false requires user-set JWT secrets.
- **NFR-6 (Data isolation)**: DEMO data (UNVERIFIED_DEMO tier) MUST be visually distinguishable and cannot drive COMPULSORY certification decisions (per FR-12/FR-13).

---

## Constraints
- **Technical**: Keep FastAPI + SQLAlchemy + SQLite/Postgres backend, React 18 + TS + Vite + Tailwind frontend. Do NOT add vector DB (keep pickle embeddings in SQLite blob for local dev; pgvector optional future work out of scope). Do NOT replace embeddings mock unless user has keys; ensure deterministic mock fallback works.
- **Business**: Do NOT invent BIS official data; all demo data UNVERIFIED_DEMO. Do NOT claim compliance certification unless OFFICIAL_BIS/OFFICIAL_GOVT evidence exists.
- **Dependencies**: Use already-installed packages ONLY. Do not add new pip/npm packages unless absolutely required and not present. If new packages required, they MUST be added to `requirements.txt` / `package.json` with rationale. (Expected: none needed — all utilities listed already installed per existing files.)

## Dependencies (Installed)
Backend: fastapi, uvicorn, sqlalchemy, alembic, python-jose[cryptography], passlib[bcrypt], python-multipart, aiofiles, PyMuPDF (fitz), python-docx, pdfplumber, pandas, pillow, pytesseract (optional), openai, tenacity, python-dotenv, pydantic-settings, numpy, bcrypt.
Frontend: react 18, react-dom, react-router-dom 6, @tanstack/react-query 5, react-hook-form, zod, axios, recharts, lucide-react, clsx, tailwind-merge, tailwindcss, typescript, vite.

## Assumptions
- Python 3.12+ available locally; Node 20+ available locally.
- SQLite file `backend/manak_ai.db` acceptable for local demo; Postgres via Docker remains for production deploy.
- Users will accept DEMO data (UNVERIFIED_DEMO badges) for labs, standards clauses, and tests until official BIS ingestion is done.
- No OpenAI/embedding keys required. ImprovedMock must give non-trivial, context-driven answers.
- Open questions below remain answered by assumptions inline until user overrides.

---

## Open Questions (Resolved with Assumptions)
- [x] Where to put new Standard Detail page? → `/standards/:id` (new route, no other page redesigned). (Resolved same as prior spec.)
- [x] Where is "Create Product" form? → Modal component rendered from CompliancePassport sidebar.
- [x] Where does chat history live? → `/knowledge` page chat sidebar (conversation sessions list).
- [x] Multilingual default behavior when translator fails? → English answer + `lang_fallback:true` flag, UI banner explaining fallback.
- [x] Where does document upload store files? → `backend/uploads/` subfolder sanitized filenames with UUID prefix. Files auto-ingested into `KnowledgeDocument` with `source_authority=UNVERIFIED_DEMO` unless admin reviews and upgrades.

---

## Acceptance Criteria

### AC-T1 — Search "curd" rejected (Section 20 Test #1)
- **Type**: `rule`
- **Given**: Demo knowledge seeded, improved retriever with `MIN_SEMANTIC_SIMILARITY=0.45` active, no dairy-related docs in DB.
- **When**: User runs `POST /knowledge/search {"query":"curd"}`.
- **Then**: Top sources do NOT contain any "stainless steel water bottle" or IS 17342 chunk. If no dairy knowledge exists, answer = "No sufficiently relevant authoritative information was found for this query in the current knowledge base." OR the "I could not find sufficient authoritative evidence to answer this confidently." sentence (whichever is correct based on the routing rules). Specifically: NO retrieved chunk has similarity < 0.45 in the returned `sources[]` array.
- **Pass Condition**: `sources[]` for "curd" query contains 0 items OR only dairy/food-related docs (if later ingested). Answer uses one of the two insufficient sentences. `confidence ∈ {INSUFFICIENT_EVIDENCE}`.
- **Evidence**: curl output of `/knowledge/search {"query":"curd"}`.

### AC-T2 — Exact IS number returns correct standard (Section 20 Test #2)
- **Type**: `rule`
- **Given**: `IS 17342:2020` exists in `standards` table.
- **When**: Search `{"query":"IS 17342:2020"}`.
- **Then**: Top 1 result standard_number == "IS 17342:2020". Exact-IS bonus ensures it beats non-standard chunks. StandardDetail page reachable at `/standards/:id` from the result and shows Title, Scope, Status all correct.
- **Pass Condition**: Top source matches `standard_number="IS 17342:2020"` and its page shows correct scope.
- **Evidence**: Search response JSON + screenshot of standard detail page.

### AC-T3 — Known product returns relevant standards ranked first (Section 20 Test #3)
- **Type**: `rule`
- **Given**: Product "Stainless Steel Water Bottle 500ml" created via UI.
- **When**: User searches `{"query":"BIS standards for stainless steel water bottle"}` (or clicks Match Standards).
- **Then**: Top standard match = IS 17342:2020, top-2 includes IS 6911 (materials) or other relevant seeded standard. No irrelevant electrical/helmet standards in top-3. Score ≥ 0.55 for IS 17342 match.
- **Pass Condition**: IS 17342 present in top-2 results of hybrid search and top-1 of product match-standards, with match_score ≥ 0.55.
- **Evidence**: Match API result + search result JSON.

### AC-T4 — Create product appears in Compliance Passport (Section 20 Test #4)
- **Type**: `rule`
- **Given**: Logged in as manufacturer role.
- **When**: Fill "Add Product" modal in CompliancePassport, submit → go back to Compliance Passport.
- **Then**: The new product row appears in the sidebar product list. Clicking it selects it and its name shows in the right pane header.
- **Pass Condition**: Row visible after submit (no page refresh needed); detail pane renders product info.
- **Evidence**: Video / screenshots of the flow.

### AC-T5 — Click Load Products shows DB products (Section 20 Test #5)
- **Type**: `rule`
- **Given**: ≥1 product in DB (from AC-T4).
- **When**: Click "Load Products" in CompliancePassport sidebar.
- **Then**: All products for the user/org appear. If 0 products → styled empty-state card "No products found. Create your first product." with CTA working.
- **Pass Condition**: Non-empty list when products exist, empty card when they don't. No "endless loading" or uncaught 401 errors in console (AuthGuard active).
- **Evidence**: Browser Network tab showing `GET /products` 200 OK + UI screenshot.

### AC-T6 — Select product → Compliance Passport loads (Section 20 Test #6)
- **Type**: `rule`
- **Given**: Product exists + has matches (Match Standards run).
- **When**: Click product in CompliancePassport sidebar.
- **Then**: Right pane renders Product info, Matched Standards list with expanded standard → summary status (6-state) + Requirements checklist items (all initially NOT_STARTED with count shown, "Not Yet Assessed" score label).
- **Pass Condition**: Matched standards list length ≥ 1, requirement checklist length ≥ 5 (after clauses+requirements seed), status shown as NOT_STARTED, score shown as text "Not Yet Assessed".
- **Evidence**: UI screenshot of compliance checklist open.

### AC-T7 — Upload document → stored + analyzed (Section 20 Test #7)
- **Type**: `rule`
- **Given**: User on DocumentAnalysis page.
- **When**: Upload a .txt file containing the string "IS 17342:2020 Clause 4.2 stainless steel material. Page 3 mentions leak test".
- **Then**: Response `standards_found` contains "IS 17342:2020"; `entities_found.clauses` contains "4.2"; `pages_found` includes `3`. If standard_id IS_17342 provided too, evidence/missing lists non-empty and `compliance_score` != 85, != fixed value (computed per FR-10 step 8). Disclaimer present on page.
- **Pass Condition**: IS found, clause/page captured, score not fixed 85.
- **Evidence**: API response JSON + UI screenshot of analysis results.

### AC-T8 — Certification question returns evidence-backed response (Section 20 Test #8)
- **Type**: `rule`
- **Given**: CertificationScheme "BIS Product Certification Scheme (ISI Mark)" seeded + linked to ≥ 1 standard with QCO evidence (or OFFICIAL_BIS seed).
- **When**: Search `{"query":"Do I need BIS certification for stainless steel water bottle?"}`.
- **Then**: Answer contains the word scheme / BIS / ISI Mark and cites the CertificationScheme source (source_authority clearly shown, at least DEMO). applicability NOT "COMPULSORY" unless OFFICIAL tier evidence exists (for demo seeds: max VOLUNTARY or NOT_DETERMINED). No hallucinated QCO names or dates.
- **Pass Condition**: Applicability != COMPULSORY for demo-tier-only data; citation includes CertificationScheme reference with authority pill visible.
- **Evidence**: Search response JSON + UI screenshot.

### AC-T9 — Unsupported question → insufficient evidence (Section 20 Test #9)
- **Type**: `rule`
- **Given**: No standards/documents for "Mars rover chassis materials".
- **When**: Search `{"query":"What BIS standard applies to Mars rover chassis?"}`.
- **Then**: Answer is EXACTLY the sentence: "I could not find sufficient authoritative evidence to answer this confidently."; `confidence = INSUFFICIENT_EVIDENCE`; `sources.length = 0` or sources are below-threshold filtered and not sent.
- **Pass Condition**: Answer string === exact insufficient-sentence text. sources empty. No hallucinated standard numbers.
- **Evidence**: Search response JSON.

### AC-T10 — Laboratory search returns verified labs only (Section 20 Test #10)
- **Type**: `rule`
- **Given**: 5 demo laboratories seeded (UNVERIFIED_DEMO badges).
- **When**: User in LabMatcher clicks Search (no filters) OR searches "Delhi NABL".
- **Then**: Returned labs = records from `laboratories` table only. `mockLabs` variable REMOVED from LabMatcher.tsx source. If laboratory table count is 0 for a given search, empty-state card shows exactly: "No verified laboratory information was found in the current knowledge base." Every displayed lab card shows DEMO badge pill or NABL/BIS badge according to its tier + lab_type enum. Contact Lab opens mailto: if email present or else disabled tooltip.
- **Pass Condition**: grep "mockLabs" in LabMatcher.tsx returns no hits; UI shows actual DB records; empty state exact text matches.
- **Evidence**: grep output + screenshots.

### Additional Rule ACs (From Core Prior Spec)

**AC-R1 (Auth)**: Register → 2xx + access_token. Login same user works. Re-register same email → 400. DB password_hash starts with bcrypt prefix `$2b$` (using the direct bcrypt implementation already done earlier).

**AC-R2 (DB init idempotent)**: `python init_db.py` succeeds. `python seed_all.py` succeeds twice in a row with no duplicate / unique-constraint errors (idempotent).

**AC-R3 (Standards detail)**: `GET /api/v1/standards` returns all seeded standards (≥ 7 after new seeds). `GET /standards/:id` returns clauses.length ≥ 3, requirements.length ≥ 5.

**AC-R4 (Product standards match)**: "Stainless Steel Water Bottle" product → POST match-standards → IS 17342 match_score > 0.2 and response includes `standard.standard_number IS 17342`.

**AC-R5 (RAG no hallucination)**: Query `{"query":"What is IS 9999:2025 about?"}` (unseeded) → confidence INSUFFICIENT_EVIDENCE, answer uses the exact insufficient-evidence sentence, NO fabricated IS 9999 details anywhere in answer or sources. Same as T9 but for IS-number hallucination case.

**AC-R6 (Compliance score computed)**: Fresh product + standard → GET summary → status NOT_STARTED, score "Not Yet Assessed". After PATCHing 2 items PASSED, 1 FAILED → status PARTIALLY_SATISFIED; score = (2 + 0)/3 = 66.7% exactly.

**AC-R7 (Doc analysis not fixed 85)**: Same as T7 but also verify compliance_score in response object is computed fraction (not always integer 85).

**AC-R8 (Labs API + no fakes)**: Same as T10 rule.

**AC-R9 (Graph real data)**: `GET /graph/data` nodes count ≥ `standards` count + `standard_clauses` count; edges count > `standards` count (actual edges not zero). Graph stats panel shows same counts as API.

**AC-R10 (Route guards + real dashboard)**: Visit `/dashboard` no token → 302 redirect to `/login`. After login dashboard shows "Welcome, <full_name>" (not "User"), stat cards show actual DB counts.

**AC-R11 (No mock UI artifacts)**: grep `setTimeout` in DocumentAnalysis.tsx → zero hits. grep `const mockLabs` in LabMatcher.tsx → zero hits. grep `const mockGraph` in KnowledgeGraph.tsx → zero hits. Match score formula: `(match.match_score || 0) * 100` (parentheses correct).

### Rubric ACs

**AC-Ru1 (Preservation fidelity 0-2)**
- 2 = all existing page titles, routes, colors, layout grids, nav links unchanged; only new sub-components and routes added.
- 1 = minor cosmetic drift (a button, class, or icon altered but user recognizes the same product).
- 0 = major redesign, new color scheme, routes renamed.
- Pass threshold ≥ 1.

**AC-Ru2 (Citation quality 0-2)**
- 2 = every RAG answer sources[] has document_title, standard_number (when applicable), page/clause/version (if known), source_authority pill in UI.
- 1 = sources present but sometimes 1 field missing.
- 0 = answers without sources.
- Pass threshold ≥ 1.

**AC-Ru3 (Error UX 0-2)**
- 2 = every page has styled error panel + retry CTA on 4xx/5xx/network; no uncaught promise rejections in console; all async submit buttons show spinner.
- 1 = error messages present but not all with retry CTAs.
- 0 = blank screens / uncaught exceptions on failures.
- Pass threshold ≥ 1.

**AC-Ru4 (Dataset clarity 0-2)**
- 2 = every seeded demo lab/standard/clause/knowledge result shows a clearly visible "DEMO / NOT OFFICIAL BIS" tag or badge in the UI.
- 1 = demo badges inconsistently shown on some cards but not all.
- 0 = demo data indistinguishable from real data.
- Pass threshold ≥ 1.

**AC-Ru5 (Evaluation dataset quality 0-2)**
- 2 = `evaluation_dataset.json` has ≥ 40 rows, covering all 7 required categories listed in FR-16, and `eval_retrieval.py` runs without errors and reports the 5 metrics against targets.
- 1 = ≥ 25 rows across 5+ categories; eval script runs; 3 of 5 metrics computed.
- 0 = eval data or script missing or won't run.
- Pass threshold ≥ 1.
