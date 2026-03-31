# Mobile App Strategy — QR Reader Django Project

## Analýza projektu

### Čo máš teraz
- Django backend (Python) so session-based autentifikáciou
- Server-side rendered HTML šablóny (Jinja2 / Django templates)
- 2 typy používateľov: **Company** (admin) a **User** (zamestnanec)
- Kľúčové funkcie:
  - QR skenovanie (kamera) + GPS poloha
  - Home Office / Business Trip / No QR skeny
  - Absencia / dovolenky
  - Firemný dashboard, analytika, dochádzka
  - Magazín (editor článkov)
  - Notifikácie (email), audit logy
  - PDF/Excel export
  - i18n: SK / DE / ES / EN

---

## Možnosti (od najjednoduchšej po najkomplexnejšiu)

---

### MOŽNOSŤ 1 — WebView wrapper (PWA alebo natívny WebView)

**Princíp:** Zabalíš existujúcu webovú aplikáciu do natívneho shell-u, ktorý otvorí tvoj web v zabudovanom prehliadači.

#### 1A — PWA (Progressive Web App) — **najrýchlejšie, 0 nového kódu**
- Pridáš `manifest.json` a Service Worker do Django
- Používatelia si nainštalujú appku priamo z prehliadača (Chrome / Safari)
- Funguje offline (čiastočne), má ikonu na ploche, fullscreen mód
- **Nevýhody:** iOS má obmedzenia (Safari WebKit, push notifikácie slabšie), nie je v App Store / Play Store

**Čo treba spraviť:**
```
1. Pridať /static/manifest.json (ikona, názov, theme_color, display: standalone)
2. Pridať Service Worker (cache statické súbory)
3. Pridať <link rel="manifest"> do base.html
4. Meta tagy pre iOS (apple-touch-icon, apple-mobile-web-app-capable)
5. Optimalizovať mobilné CSS (už máš mobile-first na scan stránke)
```

**Odhad práce:** 1–2 dni  
**Výsledok:** Inštalovateľná appka, funguje bez App Store

---

#### 1B — Capacitor (Ionic) WebView wrapper — **App Store + Play Store**
- Capacitor zabalí tvoju existujúcu web URL do natívneho Android / iOS appa
- Appka sa distribuuje cez Google Play a Apple App Store
- Natívny prístup ku kamere, GPS, notifikáciám cez Capacitor pluginy
- **Tvoj Django backend ostáva 100% nezmenený**
- UI ostáva presne rovnaké ako web

**Čo treba spraviť:**
```
1. npm init + npm install @capacitor/core @capacitor/cli @capacitor/android @capacitor/ios
2. Nakonfigurovať capacitor.config.ts (server URL = https://tvoja-domena.sk)
3. npx cap add android + npx cap add ios
4. Otvoriť Android Studio / Xcode a publishnúť
5. Voliteľne: Capacitor Camera plugin pre natívnejší QR scanner
```

**Odhad práce:** 2–5 dní (+ čas App Store review)  
**Výsledok:** Plnohodnotná appka v oboch obchodoch, UI = tvoj web  
**Nevýhoda:** Django musí byť na verejnej HTTPS doméne (nie localhost)

---

#### 1C — React Native WebView
- Jednoduchá React Native appka s `<WebView url="https://tvoj-server.sk" />`
- Takmer rovnaké ako Capacitor, ale vyžaduje React Native setup
- **Menej výhodné ako Capacitor** pre tento use case

---

### MOŽNOSŤ 2 — Hybrid: Django REST API + mobilný frontend

**Princíp:** Zo session-based Django urobíš REST API (token auth), a napíšeš nový mobilný frontend.

#### 2A — React Native (Expo) — **odporúčané ak chceš natívny feel**
- Django: Pridáš `djangorestframework` + `rest_framework.authtoken` alebo JWT
- Konvertuješ hlavné endpointy na API (scan, dashboard, absencia)
- Frontend: nová React Native appka (Expo = jednoduchší setup)
- **Výhody:** Skutočne natívne komponenty, najlepší výkon, najlepšia UX
- **Nevýhody:** Musíš prepísať celý UI, je to veľa práce

**Odhadovaná práca:** 4–8 týždňov (full rewrite UI)

---

#### 2B — Flutter — **ak chceš jedno codebase pre Android + iOS**
- Dart + Flutter = jeden kód, build pre oba OS
- Django ostane ako API backend
- Výborne vyzerá, skvelý výkon
- **Nevýhody:** Nový jazyk (Dart), full rewrite UI

**Odhadovaná práca:** 4–8 týždňov

---

### MOŽNOSŤ 3 — Expo DOM Components (React Native + Web hybrid)

- Relatívne nová možnosť (2024+): React Native s DOM komponentmi
- Môžeš repoužiť časti HTML/CSS zo svojich Django šablón
- Menej praktické pre Django projekt

---

## Porovnávacia tabuľka

| | PWA | Capacitor wrapper | React Native | Flutter |
|---|---|---|---|---|
| **Práca** | 1–2 dni | 3–5 dní | 4–8 týždňov | 4–8 týždňov |
| **UI zmeny** | Žiadne | Žiadne / minimálne | Kompletný rewrite | Kompletný rewrite |
| **Backend zmeny** | Žiadne | Žiadne | REST API | REST API |
| **App Store** | ❌ (len browser) | ✅ | ✅ | ✅ |
| **Natívna kamera** | Čiastočne | ✅ (plugin) | ✅ | ✅ |
| **GPS** | ✅ | ✅ | ✅ | ✅ |
| **Push notifikácie** | Obmedzené | ✅ | ✅ | ✅ |
| **Offline** | Čiastočne | Čiastočne | ✅ | ✅ |
| **iOS App Store** | ❌ | ✅ | ✅ | ✅ |
| **Výkon** | Web | Web | Natívny | Natívny |

---

## Moje odporúčanie pre tento projekt

### Krok 1 (teraz): PWA
- 1–2 dni práce, nulové riziko
- Používatelia si môžu nainštalovať appku na telefón
- Funguje okamžite aj s existujúcim localhost setupom

### Krok 2 (ak treba App Store): Capacitor
- Tvoj Django web ostáva nezmenený
- Capacitor ho zabalí do natívnej appky
- Scan stránka (`/user/scan/`) už je mobile-first optimalizovaná
- html5-qrcode knižnica funguje v Capacitor WebView
- **Toto je najčistejšia cesta** — minimálna práca, maximálny výsledok

### Krok 3 (dlhodobé riešenie ak chceš top UX): React Native + DRF
- Pridáš Django REST Framework
- Napíšeš novú Expo appku len pre **User** rolu (scan, dashboard, absencia)
- **Company dashboard** ostane ako web (tam je komplexná analytika, PDF export atď.)

---

## Konkrétne: čo treba pre Capacitor

### Predpoklady
- Tvoj server musí byť na verejnej HTTPS URL (nie localhost)
- Doménové meno (napr. `qrreader.firma.sk`)

### Technický postup
```bash
# 1. Inštalácia
npm install -g @capacitor/cli
mkdir mobile_app && cd mobile_app
npm init -y
npm install @capacitor/core @capacitor/android @capacitor/ios

# 2. Init
npx cap init "QR Reader" "sk.firma.qrreader" --web-dir=www

# 3. Config (capacitor.config.json)
{
  "appId": "sk.firma.qrreader",
  "appName": "QR Reader",
  "server": {
    "url": "https://qrreader.firma.sk",
    "cleartext": false
  }
}

# 4. Pridaj platformy
npx cap add android
npx cap add ios

# 5. Otvor IDE
npx cap open android  # Android Studio
npx cap open ios      # Xcode (len na Mac)
```

### Výsledok
- Appka otvorí tvoj web v natívnom WebView
- Kamera a GPS fungujú (rovnaké permisie ako v prehliadači, ale natívne dialógy)
- UI je 100% identické s webom
- Môžeš publikovať do Google Play a App Store

---

## Konkrétne: čo treba pre PWA

### Súbory na vytvorenie
1. `/static/manifest.json`
2. `/static/sw.js` (Service Worker)
3. Úpravy v `base.html` (3 riadky meta tagov)

### manifest.json (príklad)
```json
{
  "name": "QR Reader",
  "short_name": "QR Reader",
  "start_url": "/sk/user/scan/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#2563eb",
  "icons": [
    { "src": "/static/images/icon.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/static/images/icon.png", "sizes": "512x512", "type": "image/png" }
  ]
}
```

---

## Záver — Moje poradie odporúčaní

1. **PWA** — urob to teraz, ihneď, zadarmo, bez App Store
2. **Capacitor wrapper** — ak zákazníci chcú App Store, minimal práca (~3-5 dní)
3. **React Native (Expo)** — ak chceš skutočne natívnu appku pre User rolu, dlhodobý projekt

**Pre 90% prípadov je Capacitor wrapper optimálna voľba** — dostaneš App Store appku, UI ostáva rovnaké, backend sa nemení a nemusíš sa učiť nový framework.
