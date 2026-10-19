# Architecture

## System overview
Polsan Leave Manager, Polsan çalışanlarının izin talebi oluşturduğu, yöneticilerin onayladığı /
reddettiği ve İK'nın izin bakiyelerini yönettiği bir web uygulamasıdır; e-posta/Excel ile yürüyen
izin sürecini tek, denetlenebilir bir sisteme taşır. Stil: **modüler monolit** — tek süreç, tek
repo, tek veritabanı; modül sınırları `import-linter` ile zorlanır. Gerekçe: tek ekip ve orta
ölçekli bir İK uygulaması için servis ayrıştırmanın maliyeti getirisinden büyük; sınırlar testle
korunduğu için ileride ayrıştırma mümkün kalır (bootstrap kararı, 2026-10-19).

Teknoloji: Python 3.12 · FastAPI (JSON API, `/api/...`) · SQLAlchemy 2.x + Alembic · SQLite ·
frontend: FastAPI'nin statik sunduğu vanilla HTML/CSS/JavaScript (ES modülleri, build adımı yok),
API ile aynı origin.

Paket düzeni:
```
app/
  main.py                  # FastAPI uygulaması, router kaydı, exception handler
  shared/                  # DomainError tabanı, ortak tipler — hiçbir modüle bağımlı değil
  modules/<module>/
    public.py              # modülün TEK dış yüzü: facade fonksiyonlar + DTO'lar
    api.py                 # FastAPI router (yalnızca kendi modülünün service'ini çağırır)
    service.py             # use-case'ler, yetki kontrolü, transaction sınırı
    domain/                # saf Python iş kuralları (BR-n)
    repository.py, models.py  # SQLAlchemy erişimi ve tablolar (modüle özel)
  static/                  # index.html, *.css, *.js
tests/unit · tests/integration · tests/e2e
```

## Modules / components and ownership

| Module | Single responsibility | Owns |
|---|---|---|
| Organization | Çalışan kayıtları ve yönetici hiyerarşisi | Çalışan, işe giriş tarihi, doğum tarihi, bağlı olduğu Yönetici |
| Leave | İzin talebi yaşam döngüsü ve onay akışı (BR-4, BR-5, BR-6, BR-7) | İzin Talebi, durum geçmişi (audit) |
| Balances | Hak ediş, bakiye ve eksi bakiye mahsubu (BR-1, BR-3) | İzin Bakiyesi (yıl bazlı hak/kullanılan/kalan), Hak Ediş kayıtları |
| Calendar | Resmi tatiller ve iş günü hesabı (BR-2) | Resmi Tatil listesi |
| Identity | Kimlik doğrulama, oturum, roller | Kullanıcı hesabı, parola hash'i, oturum, rol ataması |

## Communication rules
- Modüller arası iletişim **yalnızca senkron facade çağrısıyla**: `app.modules.<m>.public`.
- MVP'de event / mesaj kuyruğu yoktur; ihtiyaç doğarsa önce ADR yazılır.
- Her modül yalnızca kendi tablolarını sorgular; başka modülün verisine referans **sadece ID** ile.
- Frontend JavaScript yalnızca kendi origin'indeki `/api/...` uçlarını `fetch` ile çağırır.

## Forbidden dependencies (make them testable)
Hepsi `pyproject.toml` `[tool.importlinter]` sözleşmeleri olarak `scripts/check` içinde
(`architecture` adımı) zorlanır; frontend kuralları review'da kontrol edilir.
1. Bir modül, başka bir modülün `public` dışındaki hiçbir alt paketini import etmez
   (`domain`, `service`, `repository`, `models`, `api`).
2. `app.modules.*.domain` şunları import etmez: `fastapi`, `starlette`, `sqlalchemy`, `httpx`.
   Domain saati okumaz ve IO yapmaz — "bugün" parametre olarak verilir (import-linter çağrıyı
   göremez; bu kısım review'da kontrol edilir).
3. `app.shared` hiçbir `app.modules.*` paketini import etmez.
4. Bir modülün `models`/`repository` paketi başka modülün tablosuna JOIN veya sorgu yapmaz
   (import yasağı 1 ile birlikte; review'da da kontrol).
5. `app/static` altındaki JS harici CDN veya üçüncü parti kütüphane yüklemez; DOM'a veri
   `textContent` ile basılır, `innerHTML` yasaktır.

## Deliberately out of scope
- Kurumsal SSO (Entra ID / Google OIDC) — Identity arayüzü arkasında, sonraki sürüm.
- Çok aşamalı onay (Yönetici + İK); MVP'de tek onaylayıcı: doğrudan Yönetici.
- Bordro/puantaj entegrasyonu, e-posta bildirimleri, mobil uygulama.
- PostgreSQL ve çoklu instance dağıtımı (SQLite seçildi; ölçek gerekirse ADR).
