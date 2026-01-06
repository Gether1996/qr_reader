# 📱 QR Reader - Systém pre evidenciu dochádzky

## 🌟 Prehľad

Pokročilý webový systém pre evidenciu dochádzky a riadenie pracovnej sily využívajúci technológiu QR kódov. Ideálny pre firmy akejkoľvek veľkosti, ktoré chcú modernizovať sledovanie pracovného času zamestnancov, správu dovoleniek a analýzu pracoviska.

## ✨ Hlavné funkcie

### 👔 Správa firiem
- **Podpora viacerých firiem** - Každá firma má svoje vlastné izolované prostredie
- **Firemný dashboard** - Centralizovaný ovládací panel pre všetky operácie
- **Nastavenia firmy** - Prispôsobiteľné pracovné politiky a nastavenia notifikácií
- **Rolovo založený prístup** - Majitelia firiem a manažéri s detailnými oprávneniami

### 👥 Správa zamestnancov
- **Registrácia zamestnancov** - Vytváranie a správa účtov zamestnancov
- **Roly manažérov** - Prideľovanie manažérov so špecifickými oprávneniami:
  - `can_edit_employees` - Správa údajov zamestnancov
  - `can_edit_qr_codes` - Správa QR kódov
  - `can_edit_absences` - Schvaľovanie/správa požiadaviek na voľno
- **Profily zamestnancov** - Detailné informácie vrátane:
  - Pracovných hodín za mesiac
  - Nastavení obednej prestávky
  - Nároku na dovolenku (prispôsobiteľné pre každého zamestnanca)
  - Nastavení notifikácií
- **Hromadné operácie** - Efektívna správa viacerých zamestnancov

### 🔲 Systém QR kódov
- **Dynamické generovanie QR** - Automatické vytvorenie unikátnych QR kódov
- **Sledovanie lokácie** - Každý QR kód priradený ku konkrétnej pracovnej lokalite
- **Správa QR kódov** - Vytváranie, úprava a deaktivácia QR kódov
- **Tlačiteľné QR kódy** - Generovanie A4 PDF na tlač a umiestnenie
- **Podpora viacerých lokalít** - Neobmedzený počet QR kódov na firmu

### ⏰ Sledovanie času
- **4 typy skenov**:
  - Príchod
  - Odchod
  - Začiatok obednej prestávky
  - Koniec obednej prestávky
- **GPS súradnice** - Zaznamenáva presnú polohu každého skenu
- **Reverzné geokódovanie** - Konverzia GPS na čitateľné adresy
- **Inteligentná logika tlačidiel** - Zobrazuje len relevantné možnosti podľa posledného skenu
- **Manuálne a automatické prestávky** - Flexibilné sledovanie prestávok
- **Sledovanie nočných hodín** - Automatický výpočet práce medzi 22:00-06:00
- **Monitorovanie v reálnom čase** - Vidíte, kto je práve v práci

### 📅 Správa neprítomnosti
- **4 typy neprítomnosti**:
  - Dovolenka
  - PN (Práceneschopnosť)
  - Lekár
  - Home Office
- **Schvaľovací proces**:
  - Zamestnanci požiadajú o voľno
  - Emailové notifikácie pre manažérov/firmu
  - Schválenie/zamietnutie s emailovým potvrdením
  - Priame schvaľovacie linky v emailoch
- **Detekcia konfliktov** - Upozorňuje na skeny počas dovolenkových dní
- **Integrácia kalendára** - Vizuálne zobrazenie neprítomností

### 📊 Analytika a reporty

#### Firemná analytika
- **Štatistiky aktuálneho obdobia**:
  - Dnešné príchody/odchody
  - Týždenné počty skenov
  - Mesačné porovnania
  - Zoznam aktuálne prítomných
- **Analýza časového obdobia** - Výber vlastného obdobia
- **Top QR kódy** - Najpoužívanejšie lokality
- **Rozdelenie pracovných hodín**:
  - Hodiny s/bez prestávok
  - Očakávané vs. skutočné hodiny
  - Výpočty nadčasov
  - Nočné hodiny
  - Hodinová dovolenka
- **Interaktívne grafy**:
  - Graf denných príchodov/odchodov
  - Hodinové rozdelenie (24h)
  - Koláčový graf využitia QR kódov

#### PDF Reporty (na šírku A4)
- **Tabuľka dennej dochádzky** s:
  - Dátum, deň v týždni
  - Časy príchodu/odchodu
  - Pracovné hodiny (HH:MM formát)
  - Čas prestávky (HH:MM formát)
  - Skenovaná QR lokalita
  - Inteligentné poznámky (sviatky, problémy, typy dovolenky)
- **Súhrnné štatistiky**:
  - Celkový počet pracovných dní
  - Očakávané hodiny (podľa zmluvy)
  - Celkové hodiny s/bez prestávok
  - Celkový čas prestávky
  - Nadčasové hodiny
  - Nočné hodiny (22:00-06:00)
  - Hodinová dovolenka
  - Priemerné hodiny za deň
  - Dovolenka/Home office dni
  - Dni s problémami
- **Detekcia sviatkov** - Automatické rozpoznanie štátnych sviatkov (SK, DE, ES, EN)
- **Unicode podpora** - Perfektné vykreslenie slovenských/nemeckých/španielskych znakov

#### Excel Reporty (.xlsx)
- Identické dáta ako PDF reporty
- Formátované tabuľky s farbami
- Jednoduché importovanie do iných systémov
- Zoraditeľné a filtrovateľné dáta

### 📧 Emailové notifikácie

#### Inteligentný notifikačný systém
- **Notifikácie skenov** - Konfigurovateľné pre firmu a manažérov:
  - Notifikácie príchodov
  - Notifikácie odchodov
- **Notifikácie dovoleniek**:
  - Notifikácie nových požiadaviek (pre manažérov s can_edit_absences)
  - Potvrdenia schválení (pre zamestnanca)
  - Notifikácie zrušení (ak zrušené pred dátumom začiatku)
  - Rôzny obsah emailu pre schválené/čakajúce/zrušené stavy
- **Štýlované HTML emaily** - Profesionálne, brandované emailové šablóny
- **Akčné linky** - Priame linky na schválenie/zobrazenie detailov
- **Viacjazyčná podpora** - Emaily v jazyku užívateľa

### 🔍 Pokročilé filtrovanie a vyhľadávanie
- **Date Range Picker** - Vizuálny výber v kalendári
- **Multi-parametrické filtre**:
  - Podľa mena zamestnanca
  - Podľa QR lokality
  - Podľa typu skenu
  - Podľa typu neprítomnosti
  - Podľa pracovného stavu (v práci/nie v práci)
- **Vyhľadávanie v reálnom čase** - Okamžité filtrovanie s datalistami
- **Zoraditeľné stĺpce** - Kliknite na hlavičku pre zoradenie (ASC/DESC)
- **Stránkovanie** - Konfigurovateľný počet položiek na stránku (10/25/50/100)
- **Perzistencia filtrov** - Zachová filtre počas navigácie

### 🔐 Bezpečnosť a audit

#### Systém auditných logov
- **Kompletné sledovanie aktivít**:
  - Všetky CRUD operácie (Create, Read, Update, Delete)
  - Udalosti prihlásenia/odhlásenia
  - Akcie schvaľovania
- **Detailné zaznamenávanie**:
  - Aktér (kto vykonal akciu)
  - Typ akcie
  - Časová pečiatka
  - Správa/popis
  - IP adresa
- **Filtrovateľné logy** - Vyhľadávanie podľa aktéra, akcie, časového obdobia
- **Pohľad firmy/manažéra** - Zobrazenie všetkých firemných aktivít
- **Pohľad užívateľa** - Zamestnanci vidia svoje vlastné logy

#### Kontrola prístupu
- **Session-based autentifikácia** - Samostatné sessions pre firmy a užívateľov
- **Kontroly oprávnení** - Každá akcia validuje oprávnenia
- **Obmedzenia manažérov** - Detailná kontrola nad tým, co môžu manažéri robiť
- **Automatické presmerovania** - Neautorizovaní užívatelia presmerovaní vhodne

### 🌍 Internacionalizácia (i18n)
- **4 jazyky**:
  - Slovenčina (SK) - Primárny
  - Angličtina (EN)
  - Nemčina (DE)
  - Španielčina (ES)
- **Prepínač jazykov** - Zmena jazyka za behu
- **Preložený obsah**:
  - UI elementy
  - Emailové šablóny
  - PDF reporty
  - Chybové hlásenia
  - Formáty dátumov

### 📱 Responzívny dizajn
- **Mobile-first** - Optimalizované pre smartfóny
- **Desktopové zobrazenia** - Plnohodnotné tabuľky a dashboardy
- **Podpora tabletov** - Adaptívne rozloženia
- **Touch-friendly** - Veľké tlačidlá a touch targety
- **QR skener** - Natívny prístup ku kamere na mobile

### 🎨 Používateľské rozhranie
- **Moderný dizajn** - Čisté, profesionálne Bootstrap 5 rozhranie
- **Farebne rozlíšené** - Vizuálne indikátory pre rôzne stavy:
  - Modrá - Info/Primárne akcie
  - Zelená - Úspech/Schválené
  - Oranžová - Varovania/PN
  - Červená - Chyby/Urgentné
  - Fialová - Návšteva lekára
- **Ikony** - Font Awesome ikony všade
- **Tmavé/Svetlé elementy** - Kontrast pre čitateľnosť
- **SweetAlert2** - Krásne potvrdzovací dialógy
- **Loading stavy** - Vizuálna spätná väzba pre všetky akcie

### 🔄 Dodatočné funkcie
- **Reset hesla** - Emailový reset hesla pre firmy
- **Auto obedné prestávky** - Voliteľné automatické odpočítanie prestávky
- **Počítadlá dní dovolenky** - Sledovanie zostávajúcich dní dovolenky
- **Kalendár sviatkov** - Rozpoznávanie sviatkov podľa krajiny
- **Home Office podpora** - Špeciálny typ neprítomnosti pre prácu na diaľku
- **Export dát** - Sťahovanie reportov vo formáte PDF/Excel
- **Správa bielych znakov** - Čisté spracovanie a validácia dát

## 🛠️ Technický stack

### Backend
- **Django 5.2.9** - Moderný Python web framework
- **Python 3.x** - Najnovšia stabilná verzia
- **MySQL Connector** - Pripojenie k databáze
- **Gunicorn** - Produkčný WSGI server

### Frontend
- **Bootstrap 5** - Responzívny CSS framework
- **JavaScript ES6+** - Moderný JavaScript
- **Font Awesome** - Knižnica ikon
- **SweetAlert2** - Krásne alerty
- **Daterangepicker** - Pokročilý výber dátumov

### PDF generovanie
- **ReportLab 4.4.7** - Profesionálne vytváranie PDF
- **DejaVu Fonty** - Podpora Unicode znakov
- **Landscape A4** - Optimalizované rozloženie

### Excel generovanie
- **OpenPyXL 3.1.5** - Vytváranie Excel súborov
- **Štýlované bunky** - Farby, fonty, okraje
- **Podpora vzorcov** - Pripravené na kalkulácie

### Dodatočné knižnice
- **QRCode 8.2** - Generovanie QR kódov
- **Pillow 12.1** - Spracovanie obrázkov
- **Requests 2.32** - HTTP knižnica pre geokódovanie
- **Holidays 0.60** - Podpora kalendára sviatkov
- **python-dotenv** - Správa premenných prostredia

### Nasadenie
- **Docker podpora** - Kontajnerizované nasadenie
- **WhiteNoise** - Servírovanie statických súborov
- **Gunicorn** - Produkčný server
- **MySQL/SQLite** - Možnosti databázy

## 📁 Štruktúra projektu

```
qr_reader/
├── viewer/                      # Hlavná aplikácia
│   ├── models.py               # Databázové modely
│   ├── views.py                # View funkcie
│   ├── admin.py                # Django admin
│   ├── templates/              # HTML šablóny
│   └── migrations/             # Databázové migrácie
├── qr_reader_django/           # Hlavné moduly
│   ├── crud.py                 # CRUD operácie
│   ├── crud_qr_code.py        # QR kód operácie
│   ├── crud_user.py           # User operácie
│   ├── crud_vacation.py       # Operácie neprítomnosti
│   ├── login_register_logout.py # Autentifikácia
│   ├── generate_pdf_excel.py  # Generovanie reportov
│   ├── audit.py               # Auditné zaznamenávanie
│   ├── settings.py            # Django nastavenia
│   └── urls.py                # URL routing
├── static/                     # Statické súbory
│   ├── css/                   # Štýly
│   ├── scripts/               # JavaScript
│   ├── fontawesome/           # Ikony
│   ├── fonts/                 # DejaVu fonty
│   └── images/                # Obrázky
├── media/                      # Nahrávky užívateľov
│   ├── qr_codes/              # Generované QR kódy
│   └── PDF/                   # Generované reporty
├── locale/                     # Preklady
│   ├── sk/                    # Slovenčina
│   ├── de/                    # Nemčina
│   └── es/                    # Španielčina
├── docker-compose.yml         # Docker konfigurácia
├── Dockerfile                 # Docker image
├── requirements.txt           # Python závislosti
└── manage.py                  # Django management

```

## 🚀 Kľúčové prípady použitia

### Malé podniky (1-50 zamestnancov)
- Jednoduché sledovanie času
- Základná správa dovoleniek
- Monitorovanie jednej lokality

### Stredné firmy (50-200 zamestnancov)
- Viaceré lokality/oddelenia
- Hierarchia manažérov
- Detailná analytika
- Compliance reportovanie

### Veľké podniky (200+ zamestnancov)
- Multi-site operácie
- Komplexné schvaľovacie procesy
- Pokročilá analytika
- Pripravené na integráciu (API možno pridať)

### Odvetvia
- ✅ Výroba
- ✅ Maloobchod
- ✅ Pohostinstvo
- ✅ Stavebníctvo
- ✅ Zdravotníctvo
- ✅ Školstvo
- ✅ Logistika
- ✅ Profesionálne služby

## 💡 Podnikové výhody

1. **Úspora nákladov**
   - Eliminácia manuálnych výkazov
   - Zníženie chýb vo výplatnej páske
   - Prevencia krádeže času
   - Minimalizácia administratívnej réžie

2. **Compliance**
   - Presné záznamy času
   - Auditné stopy
   - Sledovanie dovoleniek
   - Regulácie pracovného času

3. **Produktivita**
   - Viditeľnosť dochádzky v reálnom čase
   - Rýchle schvaľovacie procesy
   - Mobilná dostupnosť
   - Automatizované výpočty

4. **Prehľady**
   - Analýza pracovných vzorov
   - Monitorovanie nadčasov
   - Využitie lokalít
   - Trendy neprítomnosti

5. **Spokojnosť zamestnancov**
   - Jednoduché používanie
   - Samoobslužné požiadavky na dovolenku
   - Transparentné sledovanie času
   - Mobilné pohodlie

## 🔒 Bezpečnostné funkcie

- ✅ Hashovanie hesiel (vstavané v Django)
- ✅ Správa sessions
- ✅ CSRF ochrana
- ✅ Prevencia SQL injection
- ✅ XSS ochrana
- ✅ Bezpečný reset hesla
- ✅ Zaznamenávanie IP adries
- ✅ Validácia oprávnení
- ✅ Soft delete (uchovanie dát)

## 📈 Škálovateľnosť

- **Databáza**: MySQL pre produkciu, ľahko škálovateľná
- **Caching**: Pripravené na Redis/Memcached
- **Load Balancing**: Gunicorn podporuje viacero workerov
- **Docker**: Jednoduché horizontálne škálovanie
- **Media Storage**: Môže byť presunutý na S3/Cloud storage
- **API Ready**: RESTful štruktúra umožňuje jednoduché pridanie API

## 🎯 Možnosti budúceho rozšírenia

- Mobilná aplikácia (React Native/Flutter)
- REST API pre integrácie
- Biometrická autentifikácia
- Rozpoznávanie tváre
- Geofencing
- Plánovanie zmien
- Integrácia miezd
- Pokročilý reportovací dashboard
- Notifikácie v reálnom čase (WebSockets)
- Push notifikácie na mobile
- Sync kalendára (Google/Outlook)
- Slack/Teams integrácia

## 📞 Podpora

- Profesionálna kódová základňa
- Dobre zdokumentované
- Modulárna architektúra
- Jednoduché rozšírenie
- Čisté oddelenie zodpovedností

## 🏆 Prečo si vybrať tento systém?

1. **Kompletné riešenie** - Všetko potrebné ihneď k dispozícii
2. **Moderná technológia** - Postavené s najnovšími nástrojmi a best practices
3. **Používateľsky prívetivé** - Intuitívne rozhraie pre všetky úrovne užívateľov
4. **Flexibilné** - Prispôsobuje sa rôznym potrebám podnikov
5. **Spoľahlivé** - Robustné spracovanie chýb a validácia
6. **Udržiavateľné** - Čistý kód, jednoduché aktualizovanie
7. **Viacjazyčné** - Pripravené pre medzinárodné podnikanie
8. **Mobile-first** - Funguje perfektne na akomkoľvek zariadení
9. **Bezpečné** - Enterprise-grade bezpečnosť
10. **Overené** - Production-ready kód

## 💰 Hodnotová ponuka

Toto nie je len systém dochádzky - je to kompletná platforma pre riadenie pracovnej sily, ktorá:
- Šetrí hodiny administratívnej práce denne
- Poskytuje presné dáta pre podnikové rozhodnutia
- Zabezpečuje súlad s pracovnými predpismi
- Škáluje sa s rastom vášho podnikania
- Vyžaduje minimálne školenie
- Funguje kdekoľvek, kedykoľvek

---

**Pripravení modernizovať správu vašej pracovnej sily?** Tento systém poskytuje všetko, čo potrebujete na sledovanie, správu a optimalizáciu času a dochádzky vášho tímu.
