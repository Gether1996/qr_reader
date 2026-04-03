# Test Coverage Report - Trakero Django Application

## ðŸ“Š PrehÄ¾ad testov

**CelkovÃ½ poÄet testovacÃ­ch tried:** 11  
**CelkovÃ½ poÄet testov:** 155  
**Pokrytie:** VÅ¡etky modely + IntegraÄnÃ© testy

---

## âœ… TestovanÃ© modely a funkcionality

### 1. Company Model (15 testov)
- âœ“ Vytvorenie company s minimÃ¡lnymi poÄ¾ami
- âœ“ Vytvorenie company so vÅ¡etkÃ½mi poÄ¾ami
- âœ“ Unique constraint na email
- âœ“ String reprezentÃ¡cia
- âœ“ Verbose name plural
- âœ“ Hashovanie hesla (set_password)
- âœ“ Overenie sprÃ¡vneho hesla (check_password)
- âœ“ Overenie nesprÃ¡vneho hesla
- âœ“ Default hodnota is_active
- âœ“ DeaktivÃ¡cia company
- âœ“ NotifikaÄnÃ© nastavenia
- âœ“ VoliteÄ¾nÃ© polia mÃ´Å¾u byÅ¥ NULL

### 2. User Model (17 testov)
- âœ“ Vytvorenie usera s minimÃ¡lnymi poÄ¾ami
- âœ“ Vytvorenie usera so vÅ¡etkÃ½mi poÄ¾ami
- âœ“ Unique constraint na email
- âœ“ String reprezentÃ¡cia
- âœ“ VzÅ¥ah s Company (forward/reverse)
- âœ“ Cascade delete pri vymazanÃ­ company
- âœ“ Hashovanie hesla
- âœ“ Overenie hesla
- âœ“ Viacero userov na company
- âœ“ Permission flags (is_manager, can_edit_*)
- âœ“ NotifikaÄnÃ© nastavenia
- âœ“ Nastavenia pracovnÃ½ch hodÃ­n
- âœ“ DeaktivÃ¡cia usera
- âœ“ VoliteÄ¾nÃ© polia mÃ´Å¾u byÅ¥ NULL

### 3. QRCodeProfile Model (13 testov)
- âœ“ Vytvorenie QR kÃ³du s minimÃ¡lnymi poÄ¾ami
- âœ“ Vytvorenie s additional_info
- âœ“ AutomatickÃ© generovanie UUID
- âœ“ UnikÃ¡tnosÅ¥ UUID
- âœ“ Unique constraint na UUID
- âœ“ AutomatickÃ© generovanie QR obrÃ¡zka
- âœ“ RegenerÃ¡cia obrÃ¡zka pri update
- âœ“ UUID sa neprepÃ­Å¡e pri update (novÃ½ test!)
- âœ“ String reprezentÃ¡cia
- âœ“ VzÅ¥ah s Company
- âœ“ Cascade delete
- âœ“ Viacero QR kÃ³dov na company
- âœ“ AktivÃ¡cia/deaktivÃ¡cia QR kÃ³dov
- âœ“ generate_uuid() metÃ³da

### 4. ScanEvent Model (23 testov)
- âœ“ Vytvorenie scan eventu s minimÃ¡lnymi poÄ¾ami
- âœ“ VÅ¡etky typy scanÅ¯ (arrival, departure, lunch_break_*)
- âœ“ Device info
- âœ“ Address field
- âœ“ Home office scany
- âœ“ Business trip scany
- âœ“ String reprezentÃ¡cia pre rÃ´zne scenÃ¡re
- âœ“ Ordering (timestamp descending)
- âœ“ VzÅ¥ah s QRCodeProfile
- âœ“ VzÅ¥ah s User
- âœ“ Cascade delete pri QR kÃ³de
- âœ“ SET_NULL pri user delete
- âœ“ Viacero scanÅ¯ na usera
- âœ“ Viacero scanÅ¯ na QR kÃ³d
- âœ“ **Geocoding (5 testov):**
  - ÃšspeÅ¡nÃ½ geocoding
  - ÄŒiastoÄnÃ© dÃ¡ta
  - API failure
  - Timeout
  - PrÃ¡zdna odpoveÄ
- âœ“ Nullable fields

### 5. Vacation Model (16 testov)
- âœ“ Vytvorenie dovolenky s minimÃ¡lnymi poÄ¾ami
- âœ“ Vytvorenie so vÅ¡etkÃ½mi poÄ¾ami (Äasy)
- âœ“ String reprezentÃ¡cia
- âœ“ Ordering (date_from descending)
- âœ“ VzÅ¥ah s User
- âœ“ Cascade delete pri user
- âœ“ Viacero dovoleniek na usera
- âœ“ **days_count property (5 testov):**
  - Viacero dnÃ­
  - Jeden deÅˆ
  - Pol dÅˆa (same day + times)
  - TÃ½Å¾deÅˆ
  - Mesiac
- âœ“ Approval workflow
- âœ“ DeaktivÃ¡cia
- âœ“ RÃ´zne typy dovoleniek
- âœ“ modified_at sa aktualizuje
- âœ“ VoliteÄ¾nÃ© polia NULL
- âœ“ PrekrÃ½vajÃºce sa obdobia (systÃ©m povoÄ¾uje)

### 6. PasswordResetToken Model (10 testov)
- âœ“ Vytvorenie tokenu
- âœ“ String reprezentÃ¡cia
- âœ“ Unique constraint na token
- âœ“ VzÅ¥ah s Company
- âœ“ Cascade delete
- âœ“ **is_valid() metÃ³da (4 testy):**
  - ÄŒerstvÃ½ token
  - PouÅ¾itÃ½ token
  - ExpirovanÃ½ token
  - PouÅ¾itÃ½ a expirovanÃ½
- âœ“ OznaÄenie ako pouÅ¾itÃ½
- âœ“ Viacero tokenov na company

### 7. AuditLog Model (11 testov)
- âœ“ Vytvorenie audit logu
- âœ“ String reprezentÃ¡cia
- âœ“ VÅ¡etky typy akciÃ­ (create, update, delete, approve, login, logout)
- âœ“ VÅ¡etky typy actorov (company, user)
- âœ“ Ordering (timestamp descending)
- âœ“ Company actions logging
- âœ“ User actions logging
- âœ“ Bez IP adresy
- âœ“ DlhÃ© sprÃ¡vy
- âœ“ Filtrovanie podÄ¾a actor_email (indexed)
- âœ“ Sledovanie viacerÃ½ch akciÃ­

### 8. Magazine Model (16 testov)
- âœ“ Vytvorenie s minimÃ¡lnymi poÄ¾ami
- âœ“ Default hodnoty (template, fonts, colors)
- âœ“ Vytvorenie so vÅ¡etkÃ½mi customizÃ¡ciami
- âœ“ String reprezentÃ¡cia
- âœ“ Ordering (modified_at descending)
- âœ“ VzÅ¥ah s Company
- âœ“ VzÅ¥ah s Creator (User)
- âœ“ Cascade delete na company
- âœ“ SET_NULL na creator delete
- âœ“ **get_categories_list() metÃ³da (3 testy):**
  - NormÃ¡lne kategÃ³rie
  - S medzerami
  - PrÃ¡zdny string
- âœ“ VÅ¡etky cover header positions (top, center, bottom)
- âœ“ Publication workflow
- âœ“ Viacero magazines na company

### 9. MagazineArticle Model (13 testov)
- âœ“ Vytvorenie s minimÃ¡lnymi poÄ¾ami
- âœ“ Vytvorenie so vÅ¡etkÃ½mi poÄ¾ami
- âœ“ String reprezentÃ¡cia
- âœ“ Ordering (magazine, order, page_number)
- âœ“ VzÅ¥ah s Magazine
- âœ“ VzÅ¥ah s Author (User)
- âœ“ Cascade delete na magazine
- âœ“ SET_NULL na author delete
- âœ“ Status choices (draft, published)
- âœ“ Main story flag
- âœ“ Secondary story flag
- âœ“ Viacero ÄlÃ¡nkov na magazine
- âœ“ Default teaser

### 10. ContentBlock Model (12 testov)
- âœ“ Vytvorenie text bloku
- âœ“ Vytvorenie image bloku
- âœ“ String reprezentÃ¡cia
- âœ“ Ordering (article, order)
- âœ“ VzÅ¥ah s Article
- âœ“ Cascade delete na article
- âœ“ VÅ¡etky alignmenty (left, center, right, justify)
- âœ“ VÅ¡etky veÄ¾kosti pÃ­sma (sm, base, lg, xl)
- âœ“ Styling options (font_family, colors, background)
- âœ“ Viacero blokov na ÄlÃ¡nok
- âœ“ ZmieÅ¡anÃ© typy blokov (text + image)

### 11. Integration Tests (9 testov)
- âœ“ **KompletnÃ½ onboarding workflow:**
  - RegistrÃ¡cia company
  - Vytvorenie QR kÃ³dov
  - Pridanie zamestnancov
- âœ“ **DennÃ½ dochÃ¡dzka workflow:**
  - PrÃ­chod
  - Lunch break start/end
  - Odchod
- âœ“ **Vacation request workflow:**
  - Vytvorenie Å¾iadosti
  - Audit log
  - SchvÃ¡lenie manaÅ¾Ã©rom
  - Audit log schvÃ¡lenia
- âœ“ **Magazine creation workflow:**
  - Vytvorenie magazine
  - HlavnÃ½ ÄlÃ¡nok s content blocks
  - VedÄ¾ajÅ¡ie ÄlÃ¡nky
  - PublikÃ¡cia
- âœ“ **Home office a business trip scenÃ¡re**
- âœ“ **Password reset workflow:**
  - Vytvorenie tokenu
  - Overenie validity
  - Reset hesla
  - OznaÄenie tokenu ako pouÅ¾itÃ½
- âœ“ **Comprehensive audit trail:**
  - Login/logout
  - CRUD operÃ¡cie
  - Multiple actions tracking
- âœ“ **Multi-company data isolation:**
  - Overenie, Å¾e company nevidia navzÃ¡jom dÃ¡ta
- âœ“ **Cascade deletion integrity:**
  - Vymazanie company vymaÅ¾e vÅ¡etko sÃºvisiace

---

## ðŸ”§ OpravenÃ© problÃ©my

### 1. Datetime handling - KOMPLETNE ZJEDNOTENÃ‰ âœ…
- **ProblÃ©m:** Projekt pouÅ¾Ã­va `USE_TZ = False`, takÅ¾e vÅ¡etky datetime musia byÅ¥ naive
- **RieÅ¡enie:** 
  - OdstrÃ¡nenÃ© Å¡peciÃ¡lne ÄasovÃ© importy
  - VÅ¡etky `datetime.now()` sÃº teraz naive
  - `PasswordResetToken.is_valid()` pouÅ¾Ã­va naive datetime - konzistentnÃ© s testami
- **DotknutÃ© testy:** VÅ¡etky testy teraz pouÅ¾Ã­vajÃº iba naive datetime
- **OverenÃ©:** V celom projekte sÃº pouÅ¾itÃ© iba Å¡tandardnÃ© datetime volania

### 2. UUID persistence test
- **PridanÃ½:** NovÃ½ test `test_qrcode_uuid_not_overwritten_on_update()`
- **ÃšÄel:** Overuje, Å¾e UUID sa negeneruje znova pri update QR kÃ³du

### 3. UUID pre-save stav
- **VylepÅ¡enÃ©:** Test `test_qrcode_uuid_auto_generation()` teraz sprÃ¡vne kontroluje truthy hodnotu

---

## ðŸ“ PoznÃ¡mky k testovaniu

### Mock-ovanÃ© sluÅ¾by:
- **Geocoding API** (Nominatim) - vÅ¡etky testy pre `get_address_from_coordinates()`
- PouÅ¾Ã­va `@patch('requests.get')` pre izolÃ¡ciu

### TestovanÃ© edge cases:
- Unique constraints violations
- Cascade deletions
- SET_NULL behavior
- Overlapping data (vacation periods)
- Empty/null optional fields
- Long text content
- Multiple relationships

### NetestovanÃ© (nie je potrebnÃ©):
- Django built-in validations (CharField max_length, EmailField format)
- Database constraints (testovanÃ© cez IntegrityError)
- Auto-generated fields (created_at, modified_at) - testovanÃ© existence

---

## ðŸš€ Spustenie testov

### VÅ¡etky testy:
```bash
python manage.py test viewer.tests -v 2
```

### KonkrÃ©tna trieda:
```bash
python manage.py test viewer.tests.CompanyModelTests -v 2
```

### S pokrytÃ­m:
```bash
coverage run --source='viewer' manage.py test viewer.tests
coverage report
coverage html
```

---

## âœ… Production Readiness Checklist

- [x] VÅ¡etky modely majÃº testy
- [x] VÅ¡etky custom metÃ³dy sÃº otestovanÃ©
- [x] VÅ¡etky vzÅ¥ahy sÃº otestovanÃ©
- [x] Cascade behavior overenÃ½
- [x] Unique constraints testovanÃ©
- [x] Edge cases pokrytÃ©
- [x] Integration tests pre real-world workflows
- [x] Data isolation medzi companies overenÃ¡
- [x] Password hashing a verification testovanÃ©
- [x] Token validation testovanÃ¡
- [x] Audit logging testovanÃ½
- [x] Datetime issues vyrieÅ¡enÃ©

**Status: âœ… READY FOR PRODUCTION TESTING**

