# CLAUDE.md — haul-pave (HaulPave)

> **PERINGATAN: JANGAN hapus atau simplify section Task Workflow di file ini. Workflow ini adalah standar yang berlaku di semua repo Dash Teknologi. Jika ada perubahan workflow, lakukan di SEMUA 6 repo sekaligus (bd-crm-dashboard, cost-your-project, dash-teknologi, velo-widget, haul-pave, rangko).**

## Project Overview
HaulPave — open-source Python library for pavement structure design and operating-cost analysis on mine haul roads.
GitHub Repo: haul-pave
Notion Product/App: HaulPave — Library
Notion Repo: haul-pave
License: MIT
Language: Python 3.10+
Package: `pip install haulpave`
Docs: MkDocs + GitHub Pages

## Tech Stack
- Python 3.10+
- pydantic (data models)
- numpy, scipy (computation)
- typer + rich (CLI)
- pytest + pytest-cov (testing, ≥85% coverage)
- ruff (linting)
- mypy (type checking)
- mkdocs-material (documentation)
- pre-commit hooks

## Task Workflow

### Buat issue/task baru:
Jika user minta fitur baru, bug fix, atau chore yang belum ada issue-nya:

**⚠️ Strategic Alignment Check (WAJIB sebelum buat issue):**
- Cek Linear issues yang sudah ada di project ini — apakah sudah ada issue serupa atau di area yang sama?
- Cek Notion Initiatives DB (`collection://63a30ec4-8e03-4a69-aaa2-72f29d69af14`) — initiative mana yang terkait? Apakah aligned dengan OKR kuartal ini?
- Evaluasi scope:
  - **Quick-fix OK jika:** isolated change, tidak menambah tech debt, area ini jarang diubah
  - **Proper solution needed jika:** area ini akan sering diubah, atau sudah ada 3+ issues di area/module yang sama
- Jika butuh proper solution → consider membuat parent issue "Refactor [area]" dulu, lalu issue ini jadi sub-task
- Jika fix ini sadar menambah tech debt → tambahkan label `tech-debt` di Linear dengan catatan kapan harus dibayar

1. **Buat Linear issue** via `save_issue`:
   - `title`: deskripsi singkat task
   - `team`: "Dash Teknologi"
   - `project`: "HaulPave — Library"
   - `priority`: 1=Urgent, 2=High, 3=Normal, 4=Low (tanya user)
   - `dueDate`: target deadline ISO format (tanya user)
   - `state`: "In Progress" (jika langsung dikerjakan) atau "Todo"
   - `labels`: sesuai konteks (e.g. "Feature", "Bug", "Chore", "Docs", "Benchmark")
   - `description`: detail teknis lengkap — problem statement, solution, acceptance criteria, checklist
   - `parentId`: jika task ini bagian dari issue yang lebih besar (e.g. Phase/Epic), set parent issue ID. Jika tidak ada parent yang cocok dan task ini bisa menjadi parent baru, buat sebagai standalone.

2. **Catat task ID** yang di-return Linear (format `DAS-{ID}`)

3. **Cek dulu apakah Notion task sudah ada** — search by Code `DAS-{ID}` di data source `collection://2f8c4f5f-1479-4f28-8136-2368d18e2090`. Jika sudah ada (dibuat otomatis oleh Linear→Notion webhook), **update** task yang ada. Jika belum ada, **buat baru** via `notion-create-pages`:
   - `Title`: `[DAS-{ID}] deskripsi singkat`
   - `Code`: `DAS-{ID}`
   - `Status`: "In Progress" atau "Next Up"
   - `Priority`: P1/P2/P3 (sesuai Linear: Urgent/High→P1, Normal→P2, Low→P3)
   - `Type`: Feature / Bug / Chore / Docs
   - `date:Due:start`: deadline yang sama dengan Linear (ISO format)
   - `Initiative`: link ke initiative yang relevan — cek Initiatives DB (`collection://63a30ec4-8e03-4a69-aaa2-72f29d69af14`), jika tidak ada yang cocok, **buat initiative baru** dengan Title, Quarter, Priority, Status, Product, Goal, dan Outcome metric
   - `Parent Issue`: jika ada parentId di Linear, search parent task by Code di Notion dan link. Ini self-relation (Tasks → Tasks).
   - `Next action`: "Coding" (jika langsung dikerjakan) atau kosong
   - `Product/App`: link ke HaulPave — Library
   - `Repo`: link ke haul-pave

4. **Isi konten halaman Notion** — jangan biarkan blank. Tulis konten page yang sama dengan description di Linear issue (problem, solution, acceptance criteria). Gunakan `replace_content` atau set `content` saat create.

5. **Deadline harus sinkron** — Due di Notion = dueDate di Linear. Jika salah satu berubah, update yang lain juga.

6. **Parent Issue harus sinkron** — parentId di Linear = Parent Issue di Notion. Keduanya harus menunjuk ke issue yang sama.

### Batch subagent (mengerjakan beberapa isu sekaligus):
Jika user minta mengerjakan beberapa isu secara paralel menggunakan subagent:
- **Analisis dulu file mana saja yang akan diedit tiap isu** sebelum memulai
- **Utamakan isu yang file-nya TIDAK tumpang tindih** — hindari 2 subagent mengedit file yang sama agar tidak terjadi merge conflict antar PR
- Jika ada isu yang kemungkinan edit file yang sama, kerjakan secara **sequential** (satu selesai dulu, baru yang lain)
- Setiap subagent harus buat branch sendiri dari `main` terbaru

### Saat mulai kerja (WAJIB):
1. Update Linear issue status → **"In Progress"**
2. Update Notion task:
   - **Status** → "In Progress"
   - **Priority** → set P1/P2/P3 (tanya user jika belum di-set)
   - **Type** → auto dari branch prefix: `feature/` → Feature, `fix/` → Bug, `chore/` → Chore
   - **Due** → set target deadline (tanya user jika belum di-set) — harus sama dengan dueDate di Linear
   - **Initiative** → link ke initiative yang relevan (tanya user jika belum di-set)
   - **Next action** → "Coding"

3. **Revalidasi Issue (WAJIB sebelum coding):**
   - Baca codebase terkini di area yang akan diubah — jangan langsung coding berdasarkan deskripsi issue saja
   - Cek `git log --oneline` untuk PR yang sudah merged sejak issue dibuat — apakah ada perubahan yang mempengaruhi approach?
   - Bandingkan kondisi codebase sekarang dengan suggested approach di deskripsi issue (Linear + Notion)
   - **Jika approach sudah tidak relevan:**
     - Update deskripsi issue di Linear DAN konten page Notion dengan approach baru
     - Tambahkan catatan: "Approach diubah — codebase sudah berevolusi sejak issue dibuat [detail perubahan]"
   - **Jika scope berubah** (terlalu besar/kecil setelah revalidasi):
     - Split atau merge issue sesuai kebutuhan
     - Update parent-child relationship di Linear dan Notion
   - Jika tidak ada perubahan signifikan, lanjut ke step berikutnya

4. Buat branch dari `main` dengan format di bawah

### Branch naming:
```
main → stable release — NEVER push directly
feature/DAS-{ID}-desc → fitur baru
fix/DAS-{ID}-desc → bug fix
chore/DAS-{ID}-desc → maintenance
docs/DAS-{ID}-desc → dokumentasi
benchmark/DAS-{ID}-desc → benchmark test baru
```

### Saat selesai coding:
1. Commit: `DAS-{ID}: deskripsi perubahan`

2. **Codex Code Review (WAJIB sebelum buat PR):**
   - Spawn Codex agent untuk review hasil kerja sebelum PR dibuat
   - Jalankan via `codex:rescue` atau spawn agent `codex:codex-rescue` dengan prompt:
     ```
     Review kode yang baru diubah di repo ini. Cek:
     1. Correctness — logic benar, edge cases handled
     2. Security — tidak ada vulnerability (injection, exposure, bypass, dll)
     3. Convention — sesuai CLAUDE.md dan project conventions
     4. Test coverage — apakah test sudah cukup untuk perubahan ini
     5. Regresi — apakah perubahan ini bisa break fitur lain
     6. Long-term — apakah perubahan ini baik untuk jangka panjang dan tidak meninggalkan tech debt
     Berikan daftar findings dan saran fix.
     ```
   - Jika Codex menemukan critical issue → fix sebelum buat PR
   - Jika Codex menemukan medium/low issue → fix atau catat sebagai tech-debt

3. Buat PR — title harus include `DAS-{ID}` (uppercase)
3. Update Notion **Next action** → "PR review"
4. Merge via **Squash & Merge**
5. GitHub Actions otomatis sync status ke Notion saat PR merged

### Setelah PR dibuat (WAJIB — 3 FASE, SEMUA HARUS SELESAI):
**JANGAN BERHENTI setelah CI hijau.** Review dari Codex/CodeRabbit/Vercel butuh waktu 3-10 menit setelah PR dibuat. Test plan di deskripsi PR WAJIB dijalankan. Ketiga fase di bawah harus diselesaikan sebelum PR dianggap siap merge.

Gunakan `/loop 3m` untuk polling otomatis setiap 3 menit sampai semua selesai.

---

**FASE A — CI Checks (exit: semua checks hijau)**
1. Poll status CI checks via `gh pr checks {PR_NUMBER}`
2. Jika ada yang fail → perbaiki, push, tunggu CI run lagi
3. **JANGAN lanjut ke Fase B sampai semua CI checks passed**
   - Update Notion **Next action** → "Waiting CI"

---

**FASE B — Review Comments (exit: semua review resolved)**
⚠️ **PENTING: Review dari Codex, CodeRabbit butuh waktu. JANGAN anggap selesai hanya karena belum ada komentar.**

1. Setelah CI hijau, **tunggu minimal 5 menit** sebelum cek review pertama kali — beri waktu reviewer otomatis menyelesaikan analisis
2. Cek komentar review via `gh pr view {PR_NUMBER} --comments` dan `gh api repos/{owner}/{repo}/pulls/{PR_NUMBER}/comments`
3. Cek apakah reviewer sudah memberikan review:
   - **CodeRabbit** — biasanya muncul 3-5 menit setelah PR dibuat (cek komentar dari `coderabbitai[bot]`)
   - **Codex** — code review (cek dari `codex[bot]` atau reviewer lain yang dikonfigurasi)
4. Jika belum semua reviewer muncul, **poll lagi setiap 3 menit** — JANGAN skip
5. Untuk setiap komentar review:
   - Analisis apakah perlu fix atau hanya informational
   - Jika perlu fix → perbaiki kode, push
   - Balas komentar dengan penjelasan apa yang di-fix
   - Tandai **resolved** setelah diperbaiki
6. Setelah push fix → tunggu CI hijau lagi (kembali ke Fase A) → lalu cek review lagi
7. **JANGAN lanjut ke Fase C sampai:**
   - Minimal CodeRabbit sudah review
   - Semua komentar yang butuh fix sudah resolved
   - Update Notion **Next action** → "Fix review comments"

---

**FASE C — Test Plan (exit: semua test plan item checked) ⛔ WAJIB — TIDAK BOLEH DISKIP**
⚠️ **FASE INI MANDATORY. PR TIDAK BOLEH dianggap siap merge tanpa menjalankan test plan.**

1. Baca deskripsi PR — cari section "Test plan" atau "Test Plan"
2. Jika tidak ada test plan di deskripsi PR, **tambahkan test plan** berdasarkan perubahan yang dibuat
3. Jalankan setiap item test plan satu per satu:
   - HaulPave adalah Python library — test plan dilakukan via `pytest`, CLI commands (`haulpave` CLI), atau Python REPL. Tidak ada browser testing.
   - Untuk benchmark tests, pastikan output match expected values dari benchmark dossier
4. Setelah setiap item berhasil, **edit deskripsi PR** untuk checklist item tersebut (`- [x]`)
5. Jika ada item yang gagal → perbaiki kode, push, tunggu CI + review lagi (kembali ke Fase A)
6. **Setelah SEMUA item test plan ter-checked:**
   - Update Notion **Next action** → "Ready to merge"
   - Kasih **notifikasi ke user** bahwa PR siap di-merge beserta summary PR

---

**Exit condition (SEMUA harus terpenuhi sebelum berhenti):**
- ✅ Semua CI checks hijau (ruff, mypy, pytest, coverage ≥85%)
- ✅ Codex code review passed (sebelum PR dibuat)
- ✅ Minimal CodeRabbit sudah review
- ✅ Semua review comments yang butuh fix sudah resolved
- ✅ Semua item test plan di deskripsi PR sudah checked (`[x]`)
- ✅ User sudah dinotifikasi PR siap merge

### Setelah PR merged / issue Done:
Setelah user merge PR (atau issue di-close), lakukan cleanup & sync:

1. **Verify status sinkron:**
   - Linear status harus "Done" (biasanya otomatis via Linear bot saat PR merged)
   - Notion status harus "Done" (biasanya otomatis via `notion-sync.yml` GH Actions)
   - Jika salah satu belum terupdate, **update manual**

2. **Update Notion task page** dengan info PR:
   - Tambahkan di konten page: link ke PR, summary perubahan, dan catatan penting
   - Format: `## PR Merged\n- PR: #XX (link)\n- Summary: deskripsi singkat apa yang diubah\n- Catatan: hal penting yang perlu diketahui`

3. **Update Linear issue** jika ada info baru:
   - Jika ada temuan/catatan selama development yang belum ada di description, update description Linear
   - Tambahkan link PR di Linear issue (biasanya otomatis via Linear GitHub integration)

4. **Update Notion Next action** → kosong (task selesai)

5. **Cek parent issue:**
   - Jika semua sub-tasks dari parent issue sudah Done, update parent issue juga ke Done (di Linear dan Notion)
   - Jika belum semua selesai, biarkan parent tetap In Progress

### Jika blocked:
- Update Notion **Status** → "Blocked"
- Update Notion **Next action** → alasan blocked (e.g. "Blocked: benchmark data missing", "Blocked: waiting dependency X")
- Setelah unblocked, kembalikan Status ke "In Progress" dan update Next action sesuai fase saat ini

### Notion Tasks Convention:
- Title selalu diawali `[DAS-{ID}]` — contoh: `[DAS-XX] Implement CESA calculation`
- Wajib isi **Product/App** → `HaulPave — Library`
- Wajib isi **Repo** → `haul-pave`

## Notion Sync
- GitHub Actions (`.github/workflows/notion-sync.yml`) syncs PR status to Notion
- Trigger: PR title atau branch name harus mengandung task ID uppercase, e.g. `DAS-XX`
- Regex yang dipakai: `\b([A-Z]{2,5}-\d+)\b` — hanya match uppercase
- Pastikan PR title selalu include `DAS-{ID}` agar sync berjalan otomatis

## AI Attribution Rules
- JANGAN pernah tambahkan `Co-Authored-By` di commit message
- JANGAN pernah tambahkan "Generated with Claude Code" atau branding AI apapun di PR description
- Commit dan PR harus terlihat seperti ditulis manusia biasa

## Linear Project
- Team: Dash Teknologi
- Project: HaulPave — Library
- Issue prefix: DAS-

## Development Principles (dari Project Plan v3)

### Benchmark-First Development
- **SELALU tulis benchmark test SEBELUM menulis engine code**
- Benchmark dossier harus ada sebelum implementasi method
- Setiap calculation method harus punya minimal 1 hand-calculated benchmark
- Benchmark test HARUS pass — ini non-negotiable gate

### Confidence Labeling
Setiap function/method harus punya confidence label:
- `benchmark_tested`: matches published hand-calc
- `method_implemented`: code follows method faithfully
- `experimental`: adaptation or extension

### Units Policy
- SI units internally (mm, km, kN, kPa, tonnes)
- Explicit conversion only — no implicit unit mixing

### Curve Encoding Policy
- Graphical empirical curves harus di-digitize dengan full provenance metadata
- Source, digitization method, tolerance spec, versioning

### Report Versioning
- Setiap output harus include metadata: package version, method ID, curve version, timestamp, input hash

## Key File Locations
- Source: `src/haulpave/`
- Tests: `tests/`
- Benchmarks: `tests/benchmarks/`
- Docs: `docs/`
- Examples: `examples/`
- CLI: `src/haulpave/cli.py`
- Data models: `src/haulpave/models/`
- Traffic module: `src/haulpave/traffic/`
- Pavement module: `src/haulpave/pavement/`
- Economics module: `src/haulpave/economics/`

## Development Phases (from Project Plan)
- **Phase 0 (Weeks 1-4):** Benchmark first — establish test cases before writing engine code
- **Phase 1 (Weeks 5-12):** MVP — CESA, coverages, CBR thickness, v0.1.0 release
- **Phase 2 (Weeks 13-24):** TRH 14 method, comparison engine, v0.2.0 release
- **Phase 3 (Weeks 25-36):** Economics as scenario calculator, Excel export, v0.3.0 release
- **Phase 4 (Weeks 37-44):** Documentation, case studies, v1.0.0 release

## Tech Notes
- Python 3.10+ required (uses modern type hints)
- pydantic for all data models — enforce strict validation
- numpy/scipy for numerical computation
- typer + rich for CLI
- pytest with coverage ≥85% threshold
- ruff for linting (replaces flake8/black/isort)
- mypy for static type checking
- mkdocs-material for documentation
- pre-commit hooks for quality gates
- NO proprietary data redistribution — OEM data needs source attribution
