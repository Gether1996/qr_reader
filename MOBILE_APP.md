# MOBILE_APP.md — Trakero Mobile App

## Overview

Trakero is a **Progressive Web App (PWA)** wrapped in a native shell using **Capacitor 6**. The WebView inside the Capacitor app points to the live server at `https://dqr.314.sk`, so every feature you deploy to the server is immediately available in the app — no APK rebuild required.

| Property | Value |
|---|---|
| App ID | `sk.qrreader.app` |
| App Name | `Trakero` |
| Server URL | `https://dqr.314.sk` |
| Capacitor version | 6.0.0 |
| Platforms | Android, iOS |

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│  Capacitor Native Shell (Android APK / iOS IPA)     │
│  ┌───────────────────────────────────────────────┐  │
│  │  WebView → https://dqr.314.sk                 │  │
│  │  ┌─────────────────────────────────────────┐  │  │
│  │  │  Django PWA Application                 │  │  │
│  │  │  ┌──────────┐  ┌────────────────────┐  │  │  │
│  │  │  │ Service  │  │  IndexedDB stores  │  │  │  │
│  │  │  │ Worker   │  │  qr-reader-queue   │  │  │  │
│  │  │  │ (sw.js)  │  │  trakero-auth      │  │  │  │
│  │  │  └──────────┘  └────────────────────┘  │  │  │
│  │  └─────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────┘  │
│  Capacitor Plugins: Geolocation · Camera · SplashScreen │
└─────────────────────────────────────────────────────┘
```

---

## Capacitor Configuration (`mobile_app/capacitor.config.json`)

```json
{
  "appId":   "sk.qrreader.app",
  "appName": "Trakero",
  "webDir":  "www",
  "server": {
    "url":          "https://dqr.314.sk",
    "cleartext":    false,
    "androidScheme": "https"
  },
  "plugins": {
    "Geolocation": { "permissions": { "location": "always" } },
    "SplashScreen": { "launchShowDuration": 1500, "backgroundColor": "#2563eb" },
    "StatusBar":   { "style": "LIGHT", "backgroundColor": "#2563eb" }
  }
}
```

**Key point:** The `server.url` is the live server. The `www/` directory only contains an `index.html` redirect placeholder — the real app is served from the network.

---

## Capacitor Plugins

| Plugin | Purpose | Version |
|---|---|---|
| `@capacitor/geolocation` | GPS coordinates for scan events | 6.x |
| `@capacitor/camera` | QR code scanning via browser camera API | 6.x |
| `@capacitor/splash-screen` | Branded splash on app launch | 6.x |
| `@capacitor/status-bar` | Status bar color (#2563eb blue) | 6.x |

---

## Permissions Required

### Android (`AndroidManifest.xml`)
- `ACCESS_FINE_LOCATION` – GPS for scan location
- `ACCESS_COARSE_LOCATION` – fallback location
- `ACCESS_BACKGROUND_LOCATION` – "always" geolocation permission
- `CAMERA` – QR code scanning

### iOS (`Info.plist`)
- `NSLocationAlwaysAndWhenInUseUsageDescription`
- `NSLocationWhenInUseUsageDescription`
- `NSCameraUsageDescription`

---

## Building

### Prerequisites
```bash
cd mobile_app
npm install
```

### Android
```bash
npm run build:android
# Opens Android Studio → Build > Generate Signed APK / Bundle
```

### iOS
```bash
npm run build:ios
# Opens Xcode → Product > Archive
```

### Sync web assets after server changes
Because the app points to the live server, a sync is only needed when Capacitor native config changes:
```bash
npm run sync
```

---

## APK Distribution (Sideloading)

The APK can be distributed without Google Play:

1. Place the signed APK at `static/apk/qr-reader.apk`
2. Users download it from `https://dqr.314.sk/download/android/`
3. Enable "Install from unknown sources" on Android
4. Install the APK

---

## PWA / Service Worker

The Service Worker (`static/sw.js`) provides the offline backbone.

### Cache Strategy

| Request type | Strategy |
|---|---|
| `/static/*` assets | Cache-first, background refresh |
| `/<lang>/user/scan/` navigation | Network-first, **cache on success** for offline |
| `/<lang>/user/login/` navigation | Network-first, **cache on success** for offline |
| All other navigation | Network-first, generic offline fallback |
| POST / API calls | Network-only (handled by offline queue) |

### Background Sync Tag
`qr-scan-sync` — registered when a scan is queued offline. The SW replays queued scans in chronological order when the device reconnects.

---

## Offline Mode — Full Reference

Trakero supports complete offline operation: users can log in without internet, record attendance, and sync automatically when connectivity is restored.

### How it works

#### 1. Token issuance (online)
Every time a user visits any page while logged in, `offline-auth.js` calls:
```
GET /api/offline-token/
```
The server returns a 60-day HMAC-SHA256-signed token containing `{user_id, company_id, user_name, exp}`. The token is stored in IndexedDB (`trakero-auth` DB, `session` store).

#### 2. Offline login
When the user opens the app without internet:
- The login page loads from Service Worker cache.
- JavaScript checks IndexedDB for a valid offline token.
- **Token found** → shows "Continue as [Name]" button → navigates to cached scan page.
- **No token** → shows "No offline access available. Connect to internet to log in."

#### 3. Offline scanning
The scan page loads from SW cache. A red **"Offline mode"** banner is shown. All scan-type buttons are enabled (server validates sequencing on sync). Scans are stored in IndexedDB (`qr-reader-queue` DB) with the offline token embedded.

#### 4. Sync on reconnect
When internet is restored, both the browser `online` event and the SW Background Sync API trigger `syncQueue()`. Each queued entry is sent to:
- **With offline token** → `POST /<lang>/user/offline-scan/` with `X-Offline-Token` header (CSRF-exempt)
- **Without offline token** (old entry) → `POST /<lang>/user/scan/` with `X-CSRFToken` header (session-based)

#### 5. Token lifecycle
| Event | Action |
|---|---|
| Successful login | `offline-auth.js` auto-fetches and stores token |
| User visits any page online (logged in) | Token refreshed silently |
| Device goes online from offline | Token refreshed |
| Explicit logout | `offlineAuth.clear()` deletes token from IndexedDB |
| Token age > 60 days | Treated as expired; user must log in online once |
| `SECRET_KEY` rotated | All tokens become invalid; users must log in online |

### Important constraints
- GPS location is **always required** — it is hardware-based (works offline).
- Scan sequencing (arrival → departure → ...) is enforced **server-side** on sync, not client-side in offline mode.
- If a scan is rejected on sync (e.g. wrong sequence), it is removed from the queue to prevent an infinite retry loop.
- The offline scan endpoint (`/user/offline-scan/`) performs identical validation to the regular scan endpoint.

---

## Key JavaScript Files

| File | Role |
|---|---|
| `static/scripts/offline-auth.js` | Manages `trakero-auth` IndexedDB; `window.offlineAuth` API |
| `static/scripts/scan-queue.js` | Manages `qr-reader-queue` IndexedDB; auto-sync with offline token support |
| `static/scripts/user-scan-qr.js` | Scan UI logic; offline mode init; GPS capture |
| `static/sw.js` | Service Worker: caching, background sync, offline page serving |

### `window.offlineAuth` API

```javascript
// Fetch token from server and store in IndexedDB (call when online)
offlineAuth.fetchAndStore()  → Promise<{token, user_id, ...} | null>

// Get stored session (returns null if expired/missing)
offlineAuth.get()            → Promise<{token, user_id, company_id, user_name, expires_at} | null>

// Persist a session manually
offlineAuth.store(token, {user_id, company_id, user_name, expires_in})  → Promise

// Clear on logout
offlineAuth.clear()          → Promise

// Check if offline scanning is possible
offlineAuth.isCapable()      → Promise<boolean>
```

### `window.scanQueue` API

```javascript
// Add scan to offline queue (auto-embeds offline token)
scanQueue.add(payload, scanUrl, csrfToken)  → Promise<id>

// Force-sync all queued scans
scanQueue.sync()             → Promise<syncedCount>

// Refresh the badge UI
scanQueue.refreshBadge()

// Get count of pending scans
scanQueue.getCount()         → Promise<count>
```

---

## Django Backend — Offline Endpoints

### `GET /api/offline-token/`
Issues an offline token for the currently logged-in user.

**Auth:** Session cookie required (`user_id` in session).

**Response:**
```json
{
  "status": "ok",
  "token": "<base64_payload>.<hmac_sig>",
  "user_id": 42,
  "company_id": 7,
  "user_name": "Ján Novák",
  "expires_in": 5184000
}
```

### `POST /<lang>/user/offline-scan/`
Submits a queued offline attendance scan.

**Auth:** `X-Offline-Token: <token>` header. No CSRF required.

**Request body:** Identical to `POST /<lang>/user/scan/`
```json
{
  "uuid":             "optional-qr-code-uuid",
  "latitude":         48.1482,
  "longitude":        17.1067,
  "scan_type":        "arrival",
  "is_home_office":   false,
  "is_business_trip": false,
  "is_no_qr":         false
}
```

**Response:** Identical to regular scan endpoint.

---

## Token Security

- Signed with Django's `SECRET_KEY` using HMAC-SHA256.
- Payload is base64url-encoded (not encrypted — contains only non-sensitive IDs and name).
- 60-day expiry enforced server-side.
- `hmac.compare_digest` used for timing-safe signature comparison.
- Rotating `SECRET_KEY` invalidates all existing offline tokens.
- Token is stored in IndexedDB (not accessible cross-origin; not in localStorage).

---

## Debugging

### Android WebView debugging
Enable in `capacitor.config.json` temporarily:
```json
"android": { "webContentsDebuggingEnabled": true }
```
Then open `chrome://inspect` in Chrome desktop.

### Check offline token in browser
Open DevTools → Application → IndexedDB → `trakero-auth` → `session` → record `current`.

### Check queued scans
DevTools → Application → IndexedDB → `qr-reader-queue` → `scans`.

### SW cache inspection
DevTools → Application → Cache Storage → `qr-reader-static-v2`.

### Force SW update
DevTools → Application → Service Workers → "Update" or "Unregister" then reload.

---

## Common Issues

| Symptom | Cause | Fix |
|---|---|---|
| Offline login button not shown | Token not yet stored (never logged in online) | Log in online at least once |
| Offline scan fails on sync (401) | Token expired (> 60 days offline) | Log in online to refresh token |
| Offline scan fails on sync (409) | Wrong scan sequence (e.g. arrival after arrival) | Expected behavior; scan removed from queue |
| GPS unavailable indoors | No satellite signal | Use "Manual Check-in" button instead |
| SW not caching login/scan page | Page not visited while online | Visit both pages while connected |
| All scan types disabled offline | Cached page had stale server-state | All buttons are re-enabled by `enableAllScanTypesOffline()` in JS |

---

## Deployment Notes

- No rebuild of the APK/IPA is needed after backend changes — the WebView always loads the live server.
- After bumping the SW cache version (`CACHE_NAME` in `sw.js`), all cached pages are invalidated and re-cached on next visit.
- The offline token endpoint (`/api/offline-token/`) is outside `i18n_patterns` (language-agnostic).
- The offline scan endpoint (`/user/offline-scan/`) is inside `i18n_patterns` and follows the standard language-prefix routing.
