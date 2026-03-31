# Test Coverage Report - QR Reader Django Application

## 📊 Prehľad testov

**Celkový počet testovacích tried:** 11  
**Celkový počet testov:** 155  
**Pokrytie:** Všetky modely + Integračné testy

---

## ✅ Testované modely a funkcionality

### 1. Company Model (15 testov)
- ✓ Vytvorenie company s minimálnymi poľami
- ✓ Vytvorenie company so všetkými poľami
- ✓ Unique constraint na email
- ✓ String reprezentácia
- ✓ Verbose name plural
- ✓ Hashovanie hesla (set_password)
- ✓ Overenie správneho hesla (check_password)
- ✓ Overenie nesprávneho hesla
- ✓ Default hodnota is_active
- ✓ Deaktivácia company
- ✓ Notifikačné nastavenia
- ✓ Voliteľné polia môžu byť NULL

### 2. User Model (17 testov)
- ✓ Vytvorenie usera s minimálnymi poľami
- ✓ Vytvorenie usera so všetkými poľami
- ✓ Unique constraint na email
- ✓ String reprezentácia
- ✓ Vzťah s Company (forward/reverse)
- ✓ Cascade delete pri vymazaní company
- ✓ Hashovanie hesla
- ✓ Overenie hesla
- ✓ Viacero userov na company
- ✓ Permission flags (is_manager, can_edit_*)
- ✓ Notifikačné nastavenia
- ✓ Nastavenia pracovných hodín
- ✓ Deaktivácia usera
- ✓ Voliteľné polia môžu byť NULL

### 3. QRCodeProfile Model (13 testov)
- ✓ Vytvorenie QR kódu s minimálnymi poľami
- ✓ Vytvorenie s additional_info
- ✓ Automatické generovanie UUID
- ✓ Unikátnosť UUID
- ✓ Unique constraint na UUID
- ✓ Automatické generovanie QR obrázka
- ✓ Regenerácia obrázka pri update
- ✓ UUID sa neprepíše pri update (nový test!)
- ✓ String reprezentácia
- ✓ Vzťah s Company
- ✓ Cascade delete
- ✓ Viacero QR kódov na company
- ✓ Aktivácia/deaktivácia QR kódov
- ✓ generate_uuid() metóda

### 4. ScanEvent Model (23 testov)
- ✓ Vytvorenie scan eventu s minimálnymi poľami
- ✓ Všetky typy scanů (arrival, departure, lunch_break_*)
- ✓ Device info
- ✓ Address field
- ✓ Home office scany
- ✓ Business trip scany
- ✓ String reprezentácia pre rôzne scenáre
- ✓ Ordering (timestamp descending)
- ✓ Vzťah s QRCodeProfile
- ✓ Vzťah s User
- ✓ Cascade delete pri QR kóde
- ✓ SET_NULL pri user delete
- ✓ Viacero scanů na usera
- ✓ Viacero scanů na QR kód
- ✓ **Geocoding (5 testov):**
  - Úspešný geocoding
  - Čiastočné dáta
  - API failure
  - Timeout
  - Prázdna odpoveď
- ✓ Nullable fields

### 5. Vacation Model (16 testov)
- ✓ Vytvorenie dovolenky s minimálnymi poľami
- ✓ Vytvorenie so všetkými poľami (časy)
- ✓ String reprezentácia
- ✓ Ordering (date_from descending)
- ✓ Vzťah s User
- ✓ Cascade delete pri user
- ✓ Viacero dovoleniek na usera
- ✓ **days_count property (5 testov):**
  - Viacero dní
  - Jeden deň
  - Pol dňa (same day + times)
  - Týždeň
  - Mesiac
- ✓ Approval workflow
- ✓ Deaktivácia
- ✓ Rôzne typy dovoleniek
- ✓ modified_at sa aktualizuje
- ✓ Voliteľné polia NULL
- ✓ Prekrývajúce sa obdobia (systém povoľuje)

### 6. PasswordResetToken Model (10 testov)
- ✓ Vytvorenie tokenu
- ✓ String reprezentácia
- ✓ Unique constraint na token
- ✓ Vzťah s Company
- ✓ Cascade delete
- ✓ **is_valid() metóda (4 testy):**
  - Čerstvý token
  - Použitý token
  - Expirovaný token
  - Použitý a expirovaný
- ✓ Označenie ako použitý
- ✓ Viacero tokenov na company

### 7. AuditLog Model (11 testov)
- ✓ Vytvorenie audit logu
- ✓ String reprezentácia
- ✓ Všetky typy akcií (create, update, delete, approve, login, logout)
- ✓ Všetky typy actorov (company, user)
- ✓ Ordering (timestamp descending)
- ✓ Company actions logging
- ✓ User actions logging
- ✓ Bez IP adresy
- ✓ Dlhé správy
- ✓ Filtrovanie podľa actor_email (indexed)
- ✓ Sledovanie viacerých akcií

### 8. Magazine Model (16 testov)
- ✓ Vytvorenie s minimálnymi poľami
- ✓ Default hodnoty (template, fonts, colors)
- ✓ Vytvorenie so všetkými customizáciami
- ✓ String reprezentácia
- ✓ Ordering (modified_at descending)
- ✓ Vzťah s Company
- ✓ Vzťah s Creator (User)
- ✓ Cascade delete na company
- ✓ SET_NULL na creator delete
- ✓ **get_categories_list() metóda (3 testy):**
  - Normálne kategórie
  - S medzerami
  - Prázdny string
- ✓ Všetky cover header positions (top, center, bottom)
- ✓ Publication workflow
- ✓ Viacero magazines na company

### 9. MagazineArticle Model (13 testov)
- ✓ Vytvorenie s minimálnymi poľami
- ✓ Vytvorenie so všetkými poľami
- ✓ String reprezentácia
- ✓ Ordering (magazine, order, page_number)
- ✓ Vzťah s Magazine
- ✓ Vzťah s Author (User)
- ✓ Cascade delete na magazine
- ✓ SET_NULL na author delete
- ✓ Status choices (draft, published)
- ✓ Main story flag
- ✓ Secondary story flag
- ✓ Viacero článkov na magazine
- ✓ Default teaser

### 10. ContentBlock Model (12 testov)
- ✓ Vytvorenie text bloku
- ✓ Vytvorenie image bloku
- ✓ String reprezentácia
- ✓ Ordering (article, order)
- ✓ Vzťah s Article
- ✓ Cascade delete na article
- ✓ Všetky alignmenty (left, center, right, justify)
- ✓ Všetky veľkosti písma (sm, base, lg, xl)
- ✓ Styling options (font_family, colors, background)
- ✓ Viacero blokov na článok
- ✓ Zmiešané typy blokov (text + image)

### 11. Integration Tests (9 testov)
- ✓ **Kompletný onboarding workflow:**
  - Registrácia company
  - Vytvorenie QR kódov
  - Pridanie zamestnancov
- ✓ **Denný dochádzka workflow:**
  - Príchod
  - Lunch break start/end
  - Odchod
- ✓ **Vacation request workflow:**
  - Vytvorenie žiadosti
  - Audit log
  - Schválenie manažérom
  - Audit log schválenia
- ✓ **Magazine creation workflow:**
  - Vytvorenie magazine
  - Hlavný článok s content blocks
  - Vedľajšie články
  - Publikácia
- ✓ **Home office a business trip scenáre**
- ✓ **Password reset workflow:**
  - Vytvorenie tokenu
  - Overenie validity
  - Reset hesla
  - Označenie tokenu ako použitý
- ✓ **Comprehensive audit trail:**
  - Login/logout
  - CRUD operácie
  - Multiple actions tracking
- ✓ **Multi-company data isolation:**
  - Overenie, že company nevidia navzájom dáta
- ✓ **Cascade deletion integrity:**
  - Vymazanie company vymaže všetko súvisiace

---

## 🔧 Opravené problémy

### 1. Datetime handling - KOMPLETNE ZJEDNOTENÉ ✅
- **Problém:** Projekt používa `USE_TZ = False`, takže všetky datetime musia byť naive
- **Riešenie:** 
  - Odstránené špeciálne časové importy
  - Všetky `datetime.now()` sú teraz naive
  - `PasswordResetToken.is_valid()` používa naive datetime - konzistentné s testami
- **Dotknuté testy:** Všetky testy teraz používajú iba naive datetime
- **Overené:** V celom projekte sú použité iba štandardné datetime volania

### 2. UUID persistence test
- **Pridaný:** Nový test `test_qrcode_uuid_not_overwritten_on_update()`
- **Účel:** Overuje, že UUID sa negeneruje znova pri update QR kódu

### 3. UUID pre-save stav
- **Vylepšené:** Test `test_qrcode_uuid_auto_generation()` teraz správne kontroluje truthy hodnotu

---

## 📝 Poznámky k testovaniu

### Mock-ované služby:
- **Geocoding API** (Nominatim) - všetky testy pre `get_address_from_coordinates()`
- Používa `@patch('requests.get')` pre izoláciu

### Testované edge cases:
- Unique constraints violations
- Cascade deletions
- SET_NULL behavior
- Overlapping data (vacation periods)
- Empty/null optional fields
- Long text content
- Multiple relationships

### Netestované (nie je potrebné):
- Django built-in validations (CharField max_length, EmailField format)
- Database constraints (testované cez IntegrityError)
- Auto-generated fields (created_at, modified_at) - testované existence

---

## 🚀 Spustenie testov

### Všetky testy:
```bash
python manage.py test viewer.tests -v 2
```

### Konkrétna trieda:
```bash
python manage.py test viewer.tests.CompanyModelTests -v 2
```

### S pokrytím:
```bash
coverage run --source='viewer' manage.py test viewer.tests
coverage report
coverage html
```

---

## ✅ Production Readiness Checklist

- [x] Všetky modely majú testy
- [x] Všetky custom metódy sú otestované
- [x] Všetky vzťahy sú otestované
- [x] Cascade behavior overený
- [x] Unique constraints testované
- [x] Edge cases pokryté
- [x] Integration tests pre real-world workflows
- [x] Data isolation medzi companies overená
- [x] Password hashing a verification testované
- [x] Token validation testovaná
- [x] Audit logging testovaný
- [x] Datetime issues vyriešené

**Status: ✅ READY FOR PRODUCTION TESTING**
