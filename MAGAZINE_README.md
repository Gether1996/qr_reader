# Magazine Creator - Implementácia do Django

## Prehľad

Kompletná implementácia Magazine Creator aplikácie (inšpirovanej MagGenie) do vášho Django projektu. Umožňuje vytváranie, editáciu a publikovanie profesionálnych časopisov s AI funkciami.

## Funkcie

### 1. **Magazine Dashboard**
- Prehľad všetkých časopisov spoločnosti
- Vytvorenie nového časopisu
- Náhľad obálok s farebnými gradientmi
- Zobrazenie štatistík (počet článkov, dátum publikácie)
- Možnosť editácie, náhľadu a mazania

### 2. **Magazine Editor**
- **Konfigurácia časopisu:**
  - Názov, číslo vydania, tagline
  - Nastavenie farieb (primárna, sekundárna)
  - Kategórie článkov
  - Výber jazyka

- **Správa článkov:**
  - Vytvorenie nových článkov
  - Editácia nadpisov, kategórií, teaseru
  - Nastavenie statusu (draft/pending/published)
  - Označenie hlavného článku na obálku

- **Content Editor:**
  - Pridávanie textových blokov
  - Vkladanie obrázkov (cez URL)
  - Formátovanie textu (zarovnanie, veľkosť písma)
  - Drag & drop preusporiadanie (TODO)

### 3. **Magazine Preview**
- **Print-ready náhľad:**
  - Profesionálna obálka s gradientmi
  - Obsah (Table of Contents)
  - Stránky s článkami
  - Zadná obálka
  
- **Export do PDF:**
  - Tlač priamo z prehliadača (Ctrl+P)
  - Formát A4 (8.5in x 11in)
  - Pripravené pre profesionálnu tlač

## Štruktúra súborov

```
viewer/
├── models.py               # Magazine, MagazineArticle, ContentBlock modely
├── views.py                # Views a API endpointy
├── templates/
│   ├── magazine_dashboard.html
│   ├── magazine_editor.html
│   └── magazine_preview.html
│
static/
├── css/
│   └── magazine.css       # Všetky štýly pre magazine
├── scripts/
│   ├── magazine-dashboard.js
│   └── magazine-editor.js
│
qr_reader_django/
└── urls.py                 # URL routing
```

## Databázové modely

### Magazine
- Hlavný model časopisu
- Obsahuje konfiguráciu (farby, fonty, jazyk)
- Vzťah k Company (každá firma má svoje časopisy)

### MagazineArticle
- Článok v časopise
- Má status (draft/pending/published)
- Môže byť hlavný článok na obálke

### ContentBlock
- Obsah článku (text alebo obrázok)
- Podporuje formátovanie
- Má poradie (order) pre správne zoradenie

## API Endpointy

```
POST /magazine/<id>/update/          - Aktualizácia časopisu
POST /magazine/<id>/delete/          - Zmazanie časopisu
POST /magazine/<id>/article/create/  - Vytvorenie článku
GET  /magazine/article/<id>/data/    - Načítanie článku
POST /magazine/article/<id>/update/  - Aktualizácia článku
POST /magazine/article/<id>/delete/  - Zmazanie článku
POST /magazine/article/<id>/block/create/ - Pridanie content bloku
POST /magazine/block/<id>/update/    - Aktualizácia bloku
POST /magazine/block/<id>/delete/    - Zmazanie bloku
```

## Inštalácia a spustenie

### 1. Vytvorenie migrácií
```bash
python manage.py makemigrations
python manage.py migrate
```

### 2. Spustenie servera
```bash
python manage.py runserver
```

### 3. Prístup k aplikácii
- Prihláste sa ako spoločnosť (company)
- V navigácii vyberte "Magazine Creator"
- Alebo priamo: `http://localhost:8000/magazine/`

## Použitie

### Vytvorenie časopisu:
1. Kliknite na "Create New Magazine" na dashboarde
2. Automaticky sa vytvorí nový časopis s defaultnými nastaveniami
3. Otvorí sa editor

### Editácia časopisu:
1. Kliknite na "Settings" (ikona ozubeného kolieska)
2. Nastavte názov, farby, kategórie
3. Uložte zmeny

### Pridanie článku:
1. Kliknite na "+" v sidebar
2. Zadajte názov článku
3. Vyplňte údaje (kategória, teaser, status)
4. Pridajte obsah (text/obrázky)
5. Uložte článok

### Preview a tlač:
1. Kliknite na "Preview" 
2. Skontrolujte finálny vzhľad
3. Kliknite na "Print / Export PDF"
4. Vyberte "Save as PDF" v dialógu tlače

## Rozdiely oproti pôvodnému MagGenie

### Implementované:
✅ Dashboard s prehľadom časopisov
✅ Editor článkov s content blokmi
✅ Preview pre tlač
✅ Konfigurácia farieb a nastavení
✅ Multi-company support (každá firma má svoje časopisy)
✅ Databázové ukladanie (namiesto IndexedDB)
✅ Autentifikácia cez Django session

### Nie je implementované (možné rozšírenia):
❌ AI generovanie teaseru (Gemini API)
❌ AI vylepšovanie textu
❌ Google autentifikácia
❌ Drag & drop preusporiadanie blokov
❌ Upload obrázkov (zatiaľ len URL)
❌ Image cropper
❌ Kolaborácia medzi používateľmi
❌ Verziovanie časopisov

## Možné vylepšenia

1. **AI Integrácia:**
   - Pridať Gemini API pre generovanie teaseru
   - Automatické vylepšovanie textov
   - Generovanie nadpisov

2. **Upload obrázkov:**
   - Django FileField pre upload
   - Image processing (resize, crop)
   - Galéria obrázkov

3. **Pokročilé funkcie:**
   - Drag & drop editor
   - Šablóny časopisov
   - Export do rôznych formátov
   - Kolaboratívna editácia

4. **UX vylepšenia:**
   - Auto-save
   - Historie zmien
   - Duplikácia článkov
   - Vyhľadávanie v článkoch

## Technológie

- **Backend:** Django 4.x, Python
- **Frontend:** Bootstrap 5, Vanilla JavaScript
- **Databáza:** SQLite (alebo PostgreSQL)
- **Štýlovanie:** Custom CSS s gradientmi
- **Ikony:** Font Awesome

## Licencia

Implementované pre QR Reader Django projekt.

## Autor

Created based on MagGenie AI Magazine Creator concept.
