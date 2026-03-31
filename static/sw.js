/**
 * QR Reader — Service Worker
 * Caches static assets for fast loading. HTML pages always fetched from network.
 */

const CACHE_NAME = 'qr-reader-static-v1';

// Static assets to pre-cache on install
const PRECACHE_ASSETS = [
    '/static/css/bootstrap.min.css',
    '/static/css/base.css',
    '/static/css/style.css',
    '/static/css/navbar.css',
    '/static/css/inline-helpers.css',
    '/static/css/app_ui.css',
    '/static/css/user_scan_qr.css',
    '/static/css/user_dashboard.css',
    '/static/css/login_register.css',
    '/static/fontawesome/css/all.min.css',
    '/static/scripts/libraries/jquery-3.6.0.min.js',
    '/static/scripts/libraries/bootstrap.bundle.min.js',
    '/static/scripts/libraries/html5-qrcode.min.js',
    '/static/scripts/general.js',
    '/static/scripts/navbar.js',
    '/static/scripts/user-scan-qr.js',
];

// Offline fallback HTML shown when network is unavailable for navigation
const OFFLINE_HTML = `<!DOCTYPE html>
<html lang="sk">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
    <meta name="theme-color" content="#2563eb">
    <title>QR Reader — Offline</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #1d4ed8, #3b82f6);
            color: white;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            text-align: center;
            padding: 32px 24px;
        }
        .icon { font-size: 64px; margin-bottom: 24px; }
        h1 { font-size: 26px; font-weight: 700; margin-bottom: 10px; }
        p { font-size: 15px; opacity: 0.8; max-width: 300px; line-height: 1.6; margin-bottom: 28px; }
        button {
            padding: 14px 32px;
            background: white;
            color: #2563eb;
            border: none;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <div class="icon">📡</div>
    <h1>Žiadne pripojenie</h1>
    <p>Nie ste pripojený k internetu. Skontrolujte Wi-Fi alebo mobilné dáta.</p>
    <button onclick="location.reload()">Skúsiť znova</button>
    <script>
        window.addEventListener('online', () => location.reload());
    </script>
</body>
</html>`;

// ─── Install: pre-cache static assets ─────────────────────────────────────────
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                // Fail silently per asset — don't block install if one asset 404s
                return Promise.allSettled(
                    PRECACHE_ASSETS.map((url) =>
                        cache.add(url).catch(() => null)
                    )
                );
            })
            .then(() => self.skipWaiting())
    );
});

// ─── Activate: clean up old caches ───────────────────────────────────────────
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys()
            .then((keys) =>
                Promise.all(
                    keys
                        .filter((key) => key !== CACHE_NAME)
                        .map((key) => caches.delete(key))
                )
            )
            .then(() => self.clients.claim())
    );
});

// ─── Fetch: cache strategy per request type ───────────────────────────────────
self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);

    // Only handle same-origin requests
    if (url.origin !== location.origin) {
        return;
    }

    // Static assets: Cache-first, update in background
    if (url.pathname.startsWith('/static/')) {
        event.respondWith(
            caches.match(request).then((cached) => {
                if (cached) {
                    // Serve from cache, refresh in background
                    fetch(request)
                        .then((response) => {
                            if (response && response.status === 200) {
                                caches.open(CACHE_NAME)
                                    .then((cache) => cache.put(request, response));
                            }
                        })
                        .catch(() => null);
                    return cached;
                }
                // Not in cache: fetch and cache
                return fetch(request).then((response) => {
                    if (response && response.status === 200) {
                        const clone = response.clone();
                        caches.open(CACHE_NAME)
                            .then((cache) => cache.put(request, clone));
                    }
                    return response;
                });
            })
        );
        return;
    }

    // HTML navigation: Network-first, offline fallback
    if (request.mode === 'navigate') {
        event.respondWith(
            fetch(request)
                .catch(() =>
                    new Response(OFFLINE_HTML, {
                        status: 200,
                        headers: { 'Content-Type': 'text/html; charset=utf-8' },
                    })
                )
        );
        return;
    }

    // API / POST requests: always network, never cache
    if (request.method !== 'GET') {
        event.respondWith(fetch(request));
        return;
    }

    // All other GET requests: network with cache fallback
    event.respondWith(
        fetch(request)
            .then((response) => {
                if (response && response.status === 200) {
                    const clone = response.clone();
                    caches.open(CACHE_NAME)
                        .then((cache) => cache.put(request, clone));
                }
                return response;
            })
            .catch(() => caches.match(request))
    );
});

// ─── Background Sync: upload queued offline scans ─────────────────────────────
// Fires when the device regains connectivity (Android Chrome + modern browsers).
// Uses the same IndexedDB store as scan-queue.js (same DB name / store name).

const SYNC_DB_NAME  = 'qr-reader-queue';
const SYNC_STORE    = 'scans';
const SYNC_TAG      = 'qr-scan-sync';

function syncOpenDB() {
    return new Promise((resolve, reject) => {
        const req = indexedDB.open(SYNC_DB_NAME, 1);
        req.onupgradeneeded = (e) => {
            const db = e.target.result;
            if (!db.objectStoreNames.contains(SYNC_STORE)) {
                db.createObjectStore(SYNC_STORE, { keyPath: 'id', autoIncrement: true });
            }
        };
        req.onsuccess  = (e) => resolve(e.target.result);
        req.onerror    = (e) => reject(e.target.error);
    });
}

function syncGetAll(db) {
    return new Promise((resolve, reject) => {
        const req = db.transaction(SYNC_STORE, 'readonly').objectStore(SYNC_STORE).getAll();
        req.onsuccess = () => resolve(req.result || []);
        req.onerror   = (e) => reject(e.target.error);
    });
}

function syncDelete(db, id) {
    return new Promise((resolve, reject) => {
        const req = db.transaction(SYNC_STORE, 'readwrite').objectStore(SYNC_STORE).delete(id);
        req.onsuccess = () => resolve();
        req.onerror   = (e) => reject(e.target.error);
    });
}

self.addEventListener('sync', (event) => {
    if (event.tag !== SYNC_TAG) return;

    event.waitUntil(
        syncOpenDB().then((db) =>
            syncGetAll(db).then((scans) => {
                // Send in chronological order
                return scans
                    .sort((a, b) => a.queued_at - b.queued_at)
                    .reduce((chain, entry) =>
                        chain.then(() =>
                            fetch(entry.scan_url, {
                                method:  'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                    'X-CSRFToken':  entry.csrf_token,
                                },
                                body: JSON.stringify(entry.payload),
                            })
                            .then((response) => {
                                // Remove from queue whether success or server error
                                // (a server error means the scan is invalid; retrying won't help)
                                if (response.status < 500) {
                                    return syncDelete(db, entry.id);
                                }
                                // 5xx → leave in queue for next sync attempt
                            })
                            .catch(() => {
                                // Network still down — abort; sync will retry
                                return Promise.reject(new Error('network'));
                            })
                        ),
                    Promise.resolve()
                    )
                    .catch(() => { /* sync will be retried automatically */ });
            })
        )
    );
});

