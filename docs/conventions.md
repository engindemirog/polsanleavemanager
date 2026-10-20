# Conventions

Buradaki her kural ya araçla zorlanır (tercih edilen) ya da review'da kontrol edilir.

## Language
<!-- Set at bootstrap (step 0) and mirrored in AGENTS.md. Changing it later is allowed — edit both
     places; existing documents are not translated retroactively. -->
- Chat language (interviews, sessions): Turkish (`tr`)
- Document language (docs/, specs, plans, ADRs, review and verify reports): Turkish (`tr`)
- Always English (protocol, not prose): ANEW core files, template headings and field labels,
  `Status:` values (Draft / Approved / In progress / Shipped), `Approved by / on:`, `Source:`.
- Code identifiers, branch names, commit messages: English (domain sözlüğündeki İngilizce
  karşılıklarla). Kullanıcıya görünen metinler (UI, hata `title`/`detail`) Türkçe.
- Agent messages (handoff summaries, refusals, `Next:` lines): chat language; command names, file
  paths and protocol fields verbatim.

## Language & framework versions
- Python 3.12 (`.python-version`, `requires-python = ">=3.12,<3.13"`), ortam ve kilit: **uv**
  (`uv.lock` commit edilir; check `--frozen` çalışır).
- FastAPI, SQLAlchemy 2.x, Alembic, Pydantic v2 — ilk feature planında eklenir, `uv.lock` ile sabit.
- Frontend: vanilla HTML/CSS/JavaScript (ES2022 modülleri), build aracı ve npm yok.
- Veritabanı: SQLite (dosya; testlerde test başına geçici dosya).

## Naming
- Python: PEP 8 — modül/fonksiyon/değişken `snake_case`, sınıf `PascalCase`, sabit `UPPER_CASE`.
- Domain tipleri sözlükteki adlarla: `LeaveRequest`, `LeaveBalance`, `PublicHoliday`...
- Hata sınıfları `<Neden>Error` (`OverlappingRequestError`), hepsi `DomainError` alt sınıfı.
- Testler: dosya `test_<davranış>.py`, fonksiyon `test_<ne>_<koşul>_<beklenen>`; BR testinin adı
  veya docstring'i kuralı anar (`BR-4`).
- API yolları: `/api/<kaynak-çoğul>` kebab-case (`/api/leave-requests`), JSON alanları `snake_case`.
- Branch ve commit: `docs/git.md`.

## Error handling
- İş kuralı ihlali → `app.shared` içindeki `DomainError` alt sınıfı fırlatılır (`code` taşır).
- Tek bir FastAPI exception handler bunu RFC 9457 `application/problem+json`'a çevirir:
  `type`, `title` (Türkçe), `status`, `detail` (Türkçe), `code` (makine okunur, İngilizce).
- Doğrulama hataları (Pydantic) 422 problem+json; yetki 401/403; bulunamadı 404.
- Beklenmeyen hata → 500 + korelasyon ID; ayrıntı yalnızca loga gider. Stack trace, SQL, dosya
  yolu ve kişisel veri kullanıcıya **asla** sızmaz.
- Frontend hataları tek bir yardımcı (`showProblem`) gösterir.

## Data rules
- İzin tarihleri `datetime.date` (saat dilimi yok, takvim günü).
- Zaman damgaları (oluşturma, karar anı) UTC, timezone-aware `datetime`; UI'da Europe/Istanbul.
- İzin miktarı `decimal.Decimal`, 0,5 adımlı — **asla float** (DB'de Numeric/metin, float değil).
- ID'ler UUID (v4).
- Silme yok: talep ve bakiye hareketleri durum değişikliği + audit kaydı ile değişir.
- Kişisel veri yalnızca sahibi modülde tutulur (doğum tarihi → Organization); loglara yazılmaz.

## Enforced by tooling
- `ruff check` — pyflakes, pycodestyle, isort, bugbear, pyupgrade, bandit (`S`), naive datetime
  yasağı (`DTZ`), simplify, ruff kuralları. `ruff format --check` — biçim.
- `mypy --strict` — `app/` için tam tip denetimi.
- Mimari test (`tests/architecture_rules.py`, grimp) — `docs/architecture.md` "Forbidden
  dependencies" 1–3; `pytest` adımında koşar.
- `uv lock --check` — `uv.lock` `pyproject.toml` ile tutarlı.
- Hepsi `scripts/check` içinde (`scripts/check.conf`).
