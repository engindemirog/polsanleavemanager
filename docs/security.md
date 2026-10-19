# Security

Her plan ve review'ın uyması gereken temel kurallar.

## Secrets
- Secrets never enter the repo, specs, prompts, or chat. `.env` is gitignored; provide `.env.example`.
- Agents never print secret values, even when debugging.
- Oturum imzalama anahtarı ve benzeri değerler ortam değişkeninden okunur; varsayılan değer yoktur
  (yoksa uygulama başlamaz).

## Input & output
- Tüm sınırlarda (HTTP gövdesi, query, path) giriş **Pydantic** modeliyle doğrulanır; doğrulanmamış
  veri service katmanına girmez.
- Veritabanı erişimi yalnızca SQLAlchemy parametreli sorgularıyla; string birleştirmeyle SQL yasak.
- Frontend: sunucudan gelen veri DOM'a yalnızca `textContent` / `setAttribute` ile basılır;
  `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `eval` yasaktır.
- Hata yanıtları stack trace, SQL, dosya yolu, kişisel veri içermez (`docs/conventions.md`).
- Yanıt başlıkları: sıkı `Content-Security-Policy` (`default-src 'self'`), `X-Content-Type-Options:
  nosniff`, `Referrer-Policy: same-origin`.

## AuthN / AuthZ
- **AuthN (MVP):** Identity modülünde yerel kullanıcı + parola; parola **argon2id** ile hash'lenir.
  Sunucu tarafı oturum, çerez `HttpOnly`, `Secure`, `SameSite=Strict`; durum değiştiren her istek
  CSRF token ister. Token `localStorage`'da tutulmaz. SSO sonraki sürüm (Identity arayüzü arkasında).
- **Roller:** Employee, Manager, HR.
- **Varsayılan RED:** her endpoint açıkça rol/sahiplik kontrolü bildirir; kontrol bildirmeyen
  endpoint'i bir test yakalar (route listesi üzerinden — ilk yetkili endpoint'le eklenir).
- **Bilinçli istisnalar** (kimlik doğrulamasız, spec 0001): açılış sayfası ve statik dosyaları
  (`app/static`), sağlık kontrolü (`/api/health`, yalnızca durum döner). Etkileşimli API
  dokümanları (`/docs`, `/redoc`, `/openapi.json`) kapalıdır. Yeni istisna = spec değişikliği.
- Yetki **service katmanında** zorlanır; UI'da düğme gizlemek yetki sayılmaz.
- Görünürlük: Employee yalnızca kendi talep ve bakiyesini; Manager yalnızca doğrudan bağlılarının
  taleplerini; HR herkesi görür. Kendi talebine karar verme yasak (BR-5).
- **KVKK:** sağlık verisi özel nitelikli kişisel veridir — hastalık izninde tanı/teşhis saklanmaz,
  yalnızca tarih aralığı ve "rapor var/yok". Kişisel veri (ad, doğum tarihi, izin nedeni) loglara
  yazılmaz; loglarda yalnızca ID.

## Dependencies
- Yeni paket yalnızca **onaylanmış bir planın içinde**, gerekçesiyle eklenir; insan onaylar.
- Lisans: MIT, BSD, Apache-2.0, PSF veya eşdeğer izin verici; GPL/AGPL yok.
- Son 12 ayda bakım görmüş olmalı; sürümler `uv.lock` ile kilitli.
- Güvenlik açığı taraması (`pip-audit`) CI'da ayrı bir job'da çalışır, `scripts/check` içinde değil
  (ağ gerektirir; check deterministik ve çevrimdışı kalır).

## Review lens
Security is a mandatory dimension of every independent review (see `prompts/review.md`), not a
separate afterthought phase.
