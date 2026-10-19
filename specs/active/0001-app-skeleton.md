# Spec 0001 — Uygulama iskeleti

- Status: In progress
- Mode: lite
- Plan: `specs/plans/0001-plan.md`

## Intent
Polsan Leave Manager'ın sonraki tüm feature'larının üzerine kurulacağı, çalışan ama henüz iş
özelliği taşımayan bir uygulama iskeleti. Geliştirici ekip ve agent'lar şunu ister: uygulama tek
komutla ayağa kalksın, kullanıcı tarayıcıda Türkçe bir açılış sayfası görsün, hatalar her yerde
aynı, Türkçe ve iç ayrıntı sızdırmayan biçimde dönsün, mimari sınırlar ve testler (birim,
entegrasyon, tarayıcı) ilk günden `scripts/check` içinde zorlansın. Başarı: sonraki feature
yalnızca kendi iş kuralını yazar, altyapı kararı vermez. Bilinçli olarak yapılmayanlar: izin,
bakiye, iş günü hesabı, kullanıcı girişi ve veritabanı — hiçbir iş özelliği bu spec'te yoktur.

## Requirements
- R-1: Uygulama, yerelde tek bir belgelenmiş komutla başlatılabilir; varsayılan olarak yalnızca
  aynı makineden erişilebilir şekilde dinler (ağa açık değildir).
- R-2: Tarayıcıda uygulamanın kök adresi açıldığında Türkçe bir açılış sayfası görünür: ürün adı
  "Polsan İzin Yönetimi" ve hizmetin yakında kullanıma açılacağını bildiren bir metin.
- R-3: Açılış sayfası yalnızca uygulamanın kendi sunduğu kaynakları kullanır; harici bir kaynak
  (CDN, yazı tipi servisi, analiz aracı) yüklemez.
- R-4: Uygulama, izleme amacıyla, kimlik doğrulama gerektirmeden "çalışıyorum" durumunu bildiren
  bir sağlık kontrolü sunar. Sağlık kontrolü yalnızca durumu bildirir; sürüm, ortam, yol veya
  başka bir iç bilgi içermez.
- R-5: Sistemdeki her hata yanıtı tek bir standart biçimdedir (`docs/conventions.md`, Error
  handling): makine okunur bir hata kodu, Türkçe başlık ve Türkçe açıklama.
- R-6: Var olmayan herhangi bir adrese (API olsun olmasın) yapılan istek "bulunamadı" hatası;
  var olan bir adrese desteklenmeyen bir yöntemle yapılan istek "yöntem desteklenmiyor" hatası
  döner — ikisi de standart biçimde.
- R-7: Beklenmeyen bir hata olduğunda kullanıcı genel bir Türkçe hata mesajı ve bir korelasyon
  kimliği alır; aynı korelasyon kimliği hatanın ayrıntısıyla birlikte loga yazılır. Yanıtta yığın
  izi (stack trace), dosya yolu, sorgu veya istisna mesajı bulunmaz. Log kaydı yalnızca korelasyon
  kimliğini, isteğin yöntemini ve yolunu, istisna türünü ve yığın izini içerir; istek gövdesi,
  çerezler ve istek başlıkları loga yazılmaz.
- R-8: Her yanıt — sayfa, sağlık kontrolü ve hata yanıtları dahil — `docs/security.md`'deki
  güvenlik başlıklarını taşır: kaynakları yalnızca kendi origin'iyle sınırlayan içerik güvenlik
  politikası, içerik türü koklamanın kapatılması, yalnızca aynı origin'e referrer gönderilmesi.
- R-9: Mimari sınırlar (`docs/architecture.md`, Forbidden dependencies 1–3) otomatik doğrulanır:
  bir ihlal `scripts/check`'i kırmızı yapar.
- R-10: `scripts/check` birim, entegrasyon ve tarayıcı (e2e) testlerini çalıştırır; hızlı profil
  e2e hariç tüm testleri, tam profil hepsini kapsar. Tarayıcı testi, test edilen uygulamayı kendisi
  başlatır ve bitişte — hata ve zaman aşımı dahil — durdurur; check sonrası hiçbir süreç kalmaz.

## User experience
- Flow: Kullanıcı tarayıcıda uygulamanın kök adresini açar → açılış sayfasını görür. Başka
  etkileşim yoktur.
- States:
  - Success: başlık "Polsan İzin Yönetimi" ve "yakında" metni görünür.
  - Empty / loading / no permission: yok — sayfa statiktir, veri yüklemez, oturum istemez.
  - Error: sayfa bulunamazsa standart hata yanıtı (R-6) döner; ayrı bir hata ekranı bu spec'te yok.
- Design reference: none — the flow above is the design. Görsel tasarım, renk ve logo yok; sade,
  okunur bir sayfa yeterli.
- Accessibility: sayfa dili Türkçe olarak bildirilir; tek bir ana başlık vardır; metin/arka plan
  kontrastı WCAG AA (≥ 4.5:1). Sayfada etkileşimli öğe yoktur; klavye yolu sonraki ekranlarla
  gelir.

## Constraints & out of scope
- Teknoloji ve paket düzeni `docs/architecture.md` ve `docs/conventions.md`'ye uyar; yeni paketler
  (`docs/security.md`, Dependencies) planda gerekçesiyle listelenir ve plan onayıyla onaylanır.
- Varsayılan RED kuralının (`docs/security.md`) bilinçli istisnası: açılış sayfası, onun statik
  dosyaları ve sağlık kontrolü kimlik doğrulama istemez. Bu istisna `docs/security.md`'ye yazılır.
- `scripts/check` residue testini iki profilde de geçer (`docs/testing.md`, Resource hygiene).
- OUT OF SCOPE: iş günü hesabı (BR-2, BR-7 → spec 0002), kimlik doğrulama ve roller, veritabanı
  bağlantısı ve migration altyapısı (ilk tabloyla gelir), çalışan/izin/bakiye özellikleri, tasarımlı
  bir hata sayfası, çok dillilik, dağıtım/üretim ortamı.

## Acceptance criteria
- [ ] AC-1 — README'de belgelenen tek komut uygulamayı yerelde başlatır; komut çalışırken açılış
  sayfası ve sağlık kontrolü aynı makineden erişilebilir; varsayılan ayarla uygulama yalnızca yerel
  döngü adresinde (loopback) dinler. (R-1)
- [ ] AC-2 — Tarayıcıda kök adres açıldığında sayfanın tek ana başlığı "Polsan İzin Yönetimi"dir ve
  "yakında" bilgisini veren Türkçe metin görünür; sayfa dili `tr` olarak bildirilir; metin/arka
  plan kontrast oranı ≥ 4.5:1'dir. (R-2, UX Success, Accessibility)
- [ ] AC-3 — Açılış sayfası yüklenirken uygulamanın kendi origin'i dışına hiçbir istek gitmez.
  (R-3)
- [ ] AC-4 — Sağlık kontrolü, oturum olmadan istendiğinde başarı durumuyla ve yalnızca "çalışıyor"
  bilgisiyle yanıt verir; yanıtta sürüm, ortam, yol veya başka bir alan yoktur. (R-4)
- [ ] AC-5 — Var olmayan bir API adresine ve var olmayan bir API dışı adrese yapılan istekler
  "bulunamadı" durumuyla, standart hata biçiminde (makine okunur kod + Türkçe başlık + Türkçe
  açıklama) yanıtlanır. (R-5, R-6, UX Error)
- [ ] AC-6 — Sağlık kontrolüne desteklenmeyen bir yöntemle yapılan istek "yöntem desteklenmiyor"
  durumuyla, standart hata biçiminde yanıtlanır. (R-5, R-6)
- [ ] AC-7 — Beklenmeyen bir hata, sunucu hatası durumuyla, standart biçimde, genel bir Türkçe
  mesaj ve bir korelasyon kimliğiyle yanıtlanır; yanıtta istisna mesajı, yığın izi veya dosya yolu
  yoktur; aynı korelasyon kimliği hata ayrıntısıyla birlikte loga yazılır; log kaydında istek
  gövdesi, çerez ve istek başlığı değeri bulunmaz. (R-5, R-7)
- [ ] AC-8 — İki ayrı beklenmeyen hata iki farklı korelasyon kimliği üretir. (R-7)
- [ ] AC-9 — Açılış sayfası, sağlık kontrolü, "bulunamadı" ve sunucu hatası yanıtlarının her biri
  R-8'deki üç güvenlik başlığını taşır. (R-8)
- [ ] AC-10 — Bir modülün başka bir modülün iç paketini import etmesi, domain katmanının web/ORM
  kütüphanesi import etmesi veya `app.shared`'in bir modülü import etmesi `scripts/check`'i
  kırmızı yapar (her kural için tekrarlanabilir gözlem). (R-9)
- [ ] AC-11 — `./scripts/check --fast` e2e testlerini çalıştırmaz, birim ve entegrasyon testlerini
  çalıştırır; `./scripts/check` e2e dahil tüm testleri çalıştırır; iki profilin test sayılarının
  toplamı tüm testlerin sayısına eşittir. (R-10)
- [ ] AC-12 — Tarayıcı testi başarısız olduğunda veya zaman aşımına uğradığında da test edilen
  uygulama durdurulur; `./scripts/residue` ve `./scripts/residue --fast` hayatta kalan süreç
  raporlamaz (check'e ait süreç yok). Hata/zaman aşımı durumu kalıcı bir kırmızı testle değil,
  tekrarlanabilir bir gözlemle kanıtlanır (geçici olarak başarısız kılınan bir e2e koşusu ardından
  süreç listesi); suite kalıcı olarak yeşil kalır. (R-10)

## Definition of Done
- [ ] Every acceptance criterion mapped to proof (test or reproducible observation)
- [ ] `scripts/check` green
- [ ] Independent review done; real findings fixed, noise rejected with written rationale
- [ ] Docs / ADRs updated if behavior or architecture changed
- [ ] Spec moved to `specs/done/` (it becomes immutable there)

## Scorecard (fill at ship — honest numbers make the process improvable)
| Metric | Value |
|---|---|
| Spec revisions | |
| Fix rounds | |
| Review findings: real / noise | |
| Regressions introduced | |
| Bugs escaped to production | |
