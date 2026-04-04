/**
 * Trakero – Offline Authentication Manager
 *
 * Manages offline tokens in IndexedDB so users can record attendance
 * without an active network connection.
 *
 * Flow:
 *  1. On every page load while online, fetchAndStore() is called to
 *     refresh the token from GET /api/offline-token/.
 *  2. The token (plus user metadata) is persisted in IndexedDB.
 *  3. When the device goes offline, get() returns the cached token.
 *  4. scan-queue.js embeds the token in every queued scan entry so
 *     the service-worker Background Sync and the online-resume sync
 *     can authenticate against /user/offline-scan/ without CSRF.
 *  5. On explicit logout, clear() removes the stored session.
 *
 * Exposes: window.offlineAuth = { fetchAndStore, get, store, clear, isCapable }
 */
(function () {
    'use strict';

    var DB_NAME    = 'trakero-auth';
    var STORE_NAME = 'session';
    var DB_VERSION = 1;
    var RECORD_KEY = 'current';
    var TOKEN_ENDPOINT = '/api/offline-token/';

    var _db = null;

    // ── IndexedDB helpers ────────────────────────────────────────────────────

    function openAuthDB() {
        return new Promise(function (resolve, reject) {
            if (_db) { resolve(_db); return; }
            var req = indexedDB.open(DB_NAME, DB_VERSION);
            req.onupgradeneeded = function (e) {
                var db = e.target.result;
                if (!db.objectStoreNames.contains(STORE_NAME)) {
                    db.createObjectStore(STORE_NAME, { keyPath: 'key' });
                }
            };
            req.onsuccess = function (e) { _db = e.target.result; resolve(_db); };
            req.onerror   = function (e) { reject(e.target.error); };
        });
    }

    function dbPut(record) {
        return openAuthDB().then(function (db) {
            return new Promise(function (resolve, reject) {
                var req = db.transaction(STORE_NAME, 'readwrite')
                            .objectStore(STORE_NAME)
                            .put(record);
                req.onsuccess = function () { resolve(); };
                req.onerror   = function (e) { reject(e.target.error); };
            });
        });
    }

    function dbGet() {
        return openAuthDB().then(function (db) {
            return new Promise(function (resolve, reject) {
                var req = db.transaction(STORE_NAME, 'readonly')
                            .objectStore(STORE_NAME)
                            .get(RECORD_KEY);
                req.onsuccess = function () { resolve(req.result || null); };
                req.onerror   = function (e) { reject(e.target.error); };
            });
        });
    }

    function dbDelete() {
        return openAuthDB().then(function (db) {
            return new Promise(function (resolve, reject) {
                var req = db.transaction(STORE_NAME, 'readwrite')
                            .objectStore(STORE_NAME)
                            .delete(RECORD_KEY);
                req.onsuccess = function () { resolve(); };
                req.onerror   = function (e) { reject(e.target.error); };
            });
        });
    }

    // ── Token expiry check ───────────────────────────────────────────────────

    function isTokenExpired(record) {
        if (!record || !record.expires_at) return true;
        // Treat as expired 1 day before actual expiry to ensure smooth refresh
        return Date.now() >= (record.expires_at - 86400000);
    }

    // ── Public API ───────────────────────────────────────────────────────────

    /**
     * Store an offline session record in IndexedDB.
     * @param {string} token       The signed offline token.
     * @param {object} userData    { user_id, company_id, user_name, expires_in }
     */
    function store(token, userData) {
        var record = {
            key:        RECORD_KEY,
            token:      token,
            user_id:    userData.user_id,
            company_id: userData.company_id,
            user_name:  userData.user_name,
            expires_at: Date.now() + (userData.expires_in || 5184000) * 1000,
            stored_at:  Date.now(),
        };
        return dbPut(record);
    }

    /**
     * Retrieve the stored offline session, or null if not present/expired.
     */
    function get() {
        return dbGet().then(function (record) {
            if (!record || isTokenExpired(record)) return null;
            return record;
        });
    }

    /**
     * Remove the offline session (call on explicit logout).
     */
    function clear() {
        return dbDelete();
    }

    /**
     * Returns true if a valid, non-expired offline token is stored.
     */
    function isCapable() {
        return get().then(function (record) { return !!record; });
    }

    /**
     * Fetch a fresh offline token from the server (requires active session)
     * and persist it to IndexedDB.  Silently no-ops when called offline or
     * when the user is not logged in (401).
     */
    function fetchAndStore() {
        if (!navigator.onLine) return Promise.resolve(null);

        return fetch(TOKEN_ENDPOINT, {
            method: 'GET',
            credentials: 'same-origin',
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
        })
            .then(function (response) {
                if (!response.ok) return null;
                return response.json();
            })
            .then(function (data) {
                if (!data || data.status !== 'ok') return null;
                return store(data.token, {
                    user_id:    data.user_id,
                    company_id: data.company_id,
                    user_name:  data.user_name,
                    expires_in: data.expires_in,
                }).then(function () { return data; });
            })
            .catch(function () { return null; });
    }

    // ── Expose ───────────────────────────────────────────────────────────────

    window.offlineAuth = {
        fetchAndStore: fetchAndStore,
        get:           get,
        store:         store,
        clear:         clear,
        isCapable:     isCapable,
    };
})();
