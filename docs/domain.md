# Domain

Kodda İngilizce karşılık kullanılır; konuşma, spec ve UI'da Türkçe terim. Aynı kelime = aynı anlam.

## Ubiquitous language

| Term | Meaning | Notes / not to be confused with |
|---|---|---|
| Çalışan (`Employee`) | Sistemde izin hakkı olan kişi | Kullanıcı hesabı (`User`, Identity) ile aynı şey değil; bir Çalışan'ın bir hesabı olur |
| Yönetici (`Manager`) | Bir Çalışan'ın **doğrudan** onaylayıcısı | Rol olarak Manager; dolaylı üstler onaylayıcı değildir |
| İK (`HR`) | Bakiyeleri, çalışanları ve tatilleri yöneten rol | Talep onaylayıcısı değildir (MVP) |
| İzin Türü (`LeaveType`) | Yıllık, Mazeret, Hastalık/Rapor, Ücretsiz | Yalnızca Yıllık izin bakiyeden düşer |
| İzin Talebi (`LeaveRequest`) | Bir Çalışan'ın belirli tarih aralığı için izin isteği | Durum: Beklemede → Onaylandı / Reddedildi / İptal Edildi |
| Beklemede (`Pending`) | Oluşturulmuş, karar bekleyen talep | Aktif talep sayılır |
| Onaylandı (`Approved`) | Yönetici onayı almış talep | Aktif talep sayılır; Yıllık izinde bakiyeden düşer |
| Reddedildi (`Rejected`) | Yönetici tarafından reddedilmiş talep | Son durum; bakiyeyi etkilemez |
| İptal Edildi (`Cancelled`) | Çalışan tarafından geri çekilmiş talep | Son durum; onaylıysa bakiye iade edilir |
| İzin Bakiyesi (`LeaveBalance`) | Çalışan + yıl için hak / kullanılan / kalan | Kalan eksi olabilir (BR-3) |
| Hak Ediş (`Accrual`) | Bir yıl için tanımlanan yıllık izin hakkı | Kıdeme ve yaşa göre (BR-1) |
| Mahsup (`Offset`) | Eksi bakiyenin bir sonraki yılın hakkından düşülmesi | BR-3 |
| Resmi Tatil (`PublicHoliday`) | İK'nın tanımladığı, iş günü sayılmayan tarih | Yarım gün tatil (arife) İK tanımına bağlı — açık karar |
| İş Günü (`WorkingDay`) | Hafta sonu ve Resmi Tatil olmayan gün | İzin süresi iş günüyle ölçülür (BR-2) |
| Birim (`LeaveUnit`) | İzin miktarı birimi: 1 = tam gün, 0,5 = yarım gün | `Decimal`, asla float |

## Business rules
- **BR-1:** Yıllık izin hakkı 4857 s. İş Kanunu md. 53'e göre kıdeme bağlıdır: 1–5 yıl (5 dahil
  değil) 14 gün, 5–15 yıl (15 dahil değil) 20 gün, 15 yıl ve üzeri 26 gün. 18 yaşında ve altında
  veya 50 yaşında ve üzerinde olan Çalışan'a en az 20 gün verilir.
- **BR-2:** İzin süresi iş günü olarak hesaplanır; hafta sonu ve Resmi Tatiller süreden düşülmez
  (sayılmaz).
- **BR-3:** Yıllık izin talebi bakiyeyi aşabilir; bakiye eksiye düşer ve eksi bakiye bir sonraki
  yılın Hak Ediş'inden mahsup edilir. Talep ekranında ve onay ekranında aşım miktarı açıkça uyarı
  olarak gösterilir. Eksi bakiye için üst sınır yoktur.
- **BR-4:** Aynı Çalışan'ın tarih aralıkları çakışan iki aktif (Beklemede veya Onaylandı) talebi
  olamaz.
- **BR-5:** Bir Çalışan kendi talebini onaylayamaz veya reddedemez.
- **BR-6:** Onaylanmış talep yalnızca başlangıç tarihinden önce iptal edilebilir; iptal, düşülen
  bakiyeyi iade eder.
- **BR-7:** Yarım gün izin desteklenir (0,5 Birim).

## Key domain invariants
- Talepler ve bakiye hareketleri silinmez; değişiklik durum geçişi + audit kaydıyla olur.
- Son durumdaki (Reddedildi, İptal Edildi) bir talep tekrar değişmez.
- Bir Çalışan'ın bir yıl için tek bir İzin Bakiyesi vardır; kalan = hak − kullanılan − mahsup.
- Hastalık izninde tanı/teşhis bilgisi saklanmaz (bkz. `docs/security.md`).
