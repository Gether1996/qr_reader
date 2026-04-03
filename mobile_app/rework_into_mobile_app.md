# Mobile App Strategy - Trakero Django Project

## AnalÃ½za projektu

### ÄŒo mÃ¡Å¡ teraz
- Django backend (Python) so session-based autentifikÃ¡ciou
- Server-side rendered HTML Å¡ablÃ³ny (Jinja2 / Django templates)
- 2 typy pouÅ¾Ã­vateÄ¾ov: **Company** (admin) a **User** (zamestnanec)
- KÄ¾ÃºÄovÃ© funkcie:
  - QR skenovanie (kamera) + GPS poloha
  - Home Office / Business Trip / No QR skeny
  - Absencia / dovolenky
  - FiremnÃ½ dashboard, analytika, dochÃ¡dzka
  - MagazÃ­n (editor ÄlÃ¡nkov)
  - NotifikÃ¡cie (email), audit logy
  - PDF/Excel export
  - i18n: SK / DE / ES / EN

---

## MoÅ¾nosti (od najjednoduchÅ¡ej po najkomplexnejÅ¡iu)

---

### MOÅ½NOSÅ¤ 1 â€” WebView wrapper (PWA alebo natÃ­vny WebView)

**PrincÃ­p:** ZabalÃ­Å¡ existujÃºcu webovÃº aplikÃ¡ciu do natÃ­vneho shell-u, ktorÃ½ otvorÃ­ tvoj web v zabudovanom prehliadaÄi.

#### 1A â€” PWA (Progressive Web App) â€” **najrÃ½chlejÅ¡ie, 0 novÃ©ho kÃ³du**
- PridÃ¡Å¡ `manifest.json` a Service Worker do Django
- PouÅ¾Ã­vatelia si nainÅ¡talujÃº appku priamo z prehliadaÄa (Chrome / Safari)
- Funguje offline (ÄiastoÄne), mÃ¡ ikonu na ploche, fullscreen mÃ³d
- **NevÃ½hody:** iOS mÃ¡ obmedzenia (Safari WebKit, push notifikÃ¡cie slabÅ¡ie), nie je v App Store / Play Store

**ÄŒo treba spraviÅ¥:**
```
1. PridaÅ¥ /static/manifest.json (ikona, nÃ¡zov, theme_color, display: standalone)
2. PridaÅ¥ Service Worker (cache statickÃ© sÃºbory)
3. PridaÅ¥ <link rel="manifest"> do base.html
4. Meta tagy pre iOS (apple-touch-icon, apple-mobile-web-app-capable)
5. OptimalizovaÅ¥ mobilnÃ© CSS (uÅ¾ mÃ¡Å¡ mobile-first na scan strÃ¡nke)
```

**Odhad prÃ¡ce:** 1â€“2 dni  
**VÃ½sledok:** InÅ¡talovateÄ¾nÃ¡ appka, funguje bez App Store

---

#### 1B â€” Capacitor (Ionic) WebView wrapper â€” **App Store + Play Store**
- Capacitor zabalÃ­ tvoju existujÃºcu web URL do natÃ­vneho Android / iOS appa
- Appka sa distribuuje cez Google Play a Apple App Store
- NatÃ­vny prÃ­stup ku kamere, GPS, notifikÃ¡ciÃ¡m cez Capacitor pluginy
- **Tvoj Django backend ostÃ¡va 100% nezmenenÃ½**
- UI ostÃ¡va presne rovnakÃ© ako web

**ÄŒo treba spraviÅ¥:**
```
1. npm init + npm install @capacitor/core @capacitor/cli @capacitor/android @capacitor/ios
2. NakonfigurovaÅ¥ capacitor.config.ts (server URL = https://tvoja-domena.sk)
3. npx cap add android + npx cap add ios
4. OtvoriÅ¥ Android Studio / Xcode a publishnÃºÅ¥
5. VoliteÄ¾ne: Capacitor Camera plugin pre natÃ­vnejÅ¡Ã­ QR scanner
```

**Odhad prÃ¡ce:** 2â€“5 dnÃ­ (+ Äas App Store review)  
**VÃ½sledok:** PlnohodnotnÃ¡ appka v oboch obchodoch, UI = tvoj web  
**NevÃ½hoda:** Django musÃ­ byÅ¥ na verejnej HTTPS domÃ©ne (nie localhost)

---

#### 1C â€” React Native WebView
- JednoduchÃ¡ React Native appka s `<WebView url="https://tvoj-server.sk" />`
- Takmer rovnakÃ© ako Capacitor, ale vyÅ¾aduje React Native setup
- **Menej vÃ½hodnÃ© ako Capacitor** pre tento use case

---

### MOÅ½NOSÅ¤ 2 â€” Hybrid: Django REST API + mobilnÃ½ frontend

**PrincÃ­p:** Zo session-based Django urobÃ­Å¡ REST API (token auth), a napÃ­Å¡eÅ¡ novÃ½ mobilnÃ½ frontend.

#### 2A â€” React Native (Expo) â€” **odporÃºÄanÃ© ak chceÅ¡ natÃ­vny feel**
- Django: PridÃ¡Å¡ `djangorestframework` + `rest_framework.authtoken` alebo JWT
- KonvertujeÅ¡ hlavnÃ© endpointy na API (scan, dashboard, absencia)
- Frontend: novÃ¡ React Native appka (Expo = jednoduchÅ¡Ã­ setup)
- **VÃ½hody:** SkutoÄne natÃ­vne komponenty, najlepÅ¡Ã­ vÃ½kon, najlepÅ¡ia UX
- **NevÃ½hody:** MusÃ­Å¡ prepÃ­saÅ¥ celÃ½ UI, je to veÄ¾a prÃ¡ce

**OdhadovanÃ¡ prÃ¡ca:** 4â€“8 tÃ½Å¾dÅˆov (full rewrite UI)

---

#### 2B â€” Flutter â€” **ak chceÅ¡ jedno codebase pre Android + iOS**
- Dart + Flutter = jeden kÃ³d, build pre oba OS
- Django ostane ako API backend
- VÃ½borne vyzerÃ¡, skvelÃ½ vÃ½kon
- **NevÃ½hody:** NovÃ½ jazyk (Dart), full rewrite UI

**OdhadovanÃ¡ prÃ¡ca:** 4â€“8 tÃ½Å¾dÅˆov

---

### MOÅ½NOSÅ¤ 3 â€” Expo DOM Components (React Native + Web hybrid)

- RelatÃ­vne novÃ¡ moÅ¾nosÅ¥ (2024+): React Native s DOM komponentmi
- MÃ´Å¾eÅ¡ repouÅ¾iÅ¥ Äasti HTML/CSS zo svojich Django Å¡ablÃ³n
- Menej praktickÃ© pre Django projekt

---

## PorovnÃ¡vacia tabuÄ¾ka

| | PWA | Capacitor wrapper | React Native | Flutter |
|---|---|---|---|---|
| **PrÃ¡ca** | 1â€“2 dni | 3â€“5 dnÃ­ | 4â€“8 tÃ½Å¾dÅˆov | 4â€“8 tÃ½Å¾dÅˆov |
| **UI zmeny** | Å½iadne | Å½iadne / minimÃ¡lne | KompletnÃ½ rewrite | KompletnÃ½ rewrite |
| **Backend zmeny** | Å½iadne | Å½iadne | REST API | REST API |
| **App Store** | âŒ (len browser) | âœ… | âœ… | âœ… |
| **NatÃ­vna kamera** | ÄŒiastoÄne | âœ… (plugin) | âœ… | âœ… |
| **GPS** | âœ… | âœ… | âœ… | âœ… |
| **Push notifikÃ¡cie** | ObmedzenÃ© | âœ… | âœ… | âœ… |
| **Offline** | ÄŒiastoÄne | ÄŒiastoÄne | âœ… | âœ… |
| **iOS App Store** | âŒ | âœ… | âœ… | âœ… |
| **VÃ½kon** | Web | Web | NatÃ­vny | NatÃ­vny |

---

## Moje odporÃºÄanie pre tento projekt

### Krok 1 (teraz): PWA
- 1â€“2 dni prÃ¡ce, nulovÃ© riziko
- PouÅ¾Ã­vatelia si mÃ´Å¾u nainÅ¡talovaÅ¥ appku na telefÃ³n
- Funguje okamÅ¾ite aj s existujÃºcim localhost setupom

### Krok 2 (ak treba App Store): Capacitor
- Tvoj Django web ostÃ¡va nezmenenÃ½
- Capacitor ho zabalÃ­ do natÃ­vnej appky
- Scan strÃ¡nka (`/user/scan/`) uÅ¾ je mobile-first optimalizovanÃ¡
- html5-qrcode kniÅ¾nica funguje v Capacitor WebView
- **Toto je najÄistejÅ¡ia cesta** â€” minimÃ¡lna prÃ¡ca, maximÃ¡lny vÃ½sledok

### Krok 3 (dlhodobÃ© rieÅ¡enie ak chceÅ¡ top UX): React Native + DRF
- PridÃ¡Å¡ Django REST Framework
- NapÃ­Å¡eÅ¡ novÃº Expo appku len pre **User** rolu (scan, dashboard, absencia)
- **Company dashboard** ostane ako web (tam je komplexnÃ¡ analytika, PDF export atÄ.)

---

## KonkrÃ©tne: Äo treba pre Capacitor

### Predpoklady
- Tvoj server musÃ­ byÅ¥ na verejnej HTTPS URL (nie localhost)
- DomÃ©novÃ© meno (napr. `qrreader.firma.sk`)

### TechnickÃ½ postup
```bash
# 1. InÅ¡talÃ¡cia
npm install -g @capacitor/cli
mkdir mobile_app && cd mobile_app
npm init -y
npm install @capacitor/core @capacitor/android @capacitor/ios

# 2. Init
npx cap init "Trakero" "sk.firma.qrreader" --web-dir=www

# 3. Config (capacitor.config.json)
{
  "appId": "sk.firma.qrreader",
  "appName": "Trakero",
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

### VÃ½sledok
- Appka otvorÃ­ tvoj web v natÃ­vnom WebView
- Kamera a GPS fungujÃº (rovnakÃ© permisie ako v prehliadaÄi, ale natÃ­vne dialÃ³gy)
- UI je 100% identickÃ© s webom
- MÃ´Å¾eÅ¡ publikovaÅ¥ do Google Play a App Store

---

## KonkrÃ©tne: Äo treba pre PWA

### SÃºbory na vytvorenie
1. `/static/manifest.json`
2. `/static/sw.js` (Service Worker)
3. Ãšpravy v `base.html` (3 riadky meta tagov)

### manifest.json (prÃ­klad)
```json
{
  "name": "Trakero",
  "short_name": "Trakero",
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

## ZÃ¡ver â€” Moje poradie odporÃºÄanÃ­

1. **PWA** â€” urob to teraz, ihneÄ, zadarmo, bez App Store
2. **Capacitor wrapper** â€” ak zÃ¡kaznÃ­ci chcÃº App Store, minimal prÃ¡ca (~3-5 dnÃ­)
3. **React Native (Expo)** â€” ak chceÅ¡ skutoÄne natÃ­vnu appku pre User rolu, dlhodobÃ½ projekt

**Pre 90% prÃ­padov je Capacitor wrapper optimÃ¡lna voÄ¾ba** â€” dostaneÅ¡ App Store appku, UI ostÃ¡va rovnakÃ©, backend sa nemenÃ­ a nemusÃ­Å¡ sa uÄiÅ¥ novÃ½ framework.

