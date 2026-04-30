## MVP Plan: Personal Study Saver (Chrome + Web Dashboard)

### Summary
Build a personal-only MVP that lets a user save coding problems and blog posts from any site through a Chrome extension, then manage everything in a centralized web dashboard.  
Start with full auth first (Google + Gmail email/password), then saving/favorites, then dashboard filtering/search.

### Implementation Changes
1. **Monorepo structure and baseline**
- Keep `apps/server` as the core API (FastAPI + PostgreSQL + SQLAlchemy).
- Build `apps/client` as the main dashboard UI (React + Vite).
- Build `apps/extension` as Manifest V3 Chrome extension (popup + content script + background service worker).
- Add shared conventions only (API contract + content type enums), no shared package complexity in MVP.

2. **Authentication (first milestone)**
- Implement auth flows:
  - `POST /auth/signup` (email/password, Gmail-only)
  - `POST /auth/login`
  - `GET /auth/google/start`
  - `GET /auth/google/callback`
  - `POST /auth/refresh`
  - `POST /auth/logout`
  - `GET /auth/me`
- Enforce Gmail-only policy:
  - Email/password signup accepts only `@gmail.com`.
  - Google OAuth accepts only verified Gmail accounts.
- Security defaults:
  - Argon2 password hashing.
  - Short-lived access token + refresh token rotation.
  - Per-device refresh token records with revocation support.

3. **Saved item capture + parser pipeline**
- Extension captures current tab URL + page metadata and sends to API.
- Use **generic parser first** for any URL:
  - title, canonical URL, site, type (`problem|blog|other`), snippet.
- Add adapters for priority sites:
  - Coding: Codeforces, CodeChef, LeetCode, AtCoder, GeeksforGeeks.
  - Blogs: Medium, Substack.
- Core item endpoints:
  - `POST /items`
  - `GET /items` (search + filters)
  - `GET /items/:id`
  - `PATCH /items/:id` (favorite, note, tags)
  - `DELETE /items/:id`
- Deduplicate per user by canonical URL; allow updates to note/tags/favorite.

4. **Dashboard + extension UX**
- Web dashboard (`apps/client`):
  - Auth screens (Google + Gmail/password).
  - List view with search, filters (site/type/favorite), sort by recent.
  - Item detail drawer/page with note + tags + favorite toggle.
  - Basic personal stats (saved count, favorites count, by source site).
- Extension (`apps/extension`):
  - Quick save button from current page.
  - Favorite toggle and optional note input in popup.
  - Auth state indicator and sign-in action.

### Public APIs / Interfaces / Types
- **Auth request/response contracts** for signup/login/google callback/refresh/me/logout.
- **SavedItem type**:
  - `id, user_id, url, canonical_url, source_site, content_type, title, snippet, metadata_json, is_favorite, note, tags, created_at, updated_at`
- **Filter contract** for `GET /items`:
  - `q, source_site, content_type, is_favorite, page, limit, sort`
- **Parser result contract** (internal/server-side):
  - `canonical_url, source_site, content_type, title, snippet, metadata_json`

### Test Plan
- **Auth tests**
  - Gmail-only enforcement for email/password signup.
  - Google login accepts verified Gmail and rejects non-Gmail.
  - Token refresh rotation and logout revocation.
- **Items API tests**
  - Save item, dedup by canonical URL, update favorite/note/tags, filter/search behavior.
- **Parser tests**
  - Generic parser works on arbitrary URLs.
  - Adapter extraction succeeds for at least one URL per target site.
- **E2E smoke flow**
  - Sign in from extension -> save page -> view in dashboard -> mark favorite -> filter favorites.

### Assumptions and Defaults
- Keep scope strictly personal (single-user private data model behavior); no group sharing in MVP.
- Keep capture simple: metadata + manual tags/notes only (no full content snapshot, no AI summaries yet).
- Use PostgreSQL from day one to avoid migration churn.
- Production deployment choices are deferred; plan targets local/dev-first implementation with clean upgrade path.
- Plan artifact file at project root: `MVP_PRODUCT_PLAN.md`.
