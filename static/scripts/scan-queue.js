/**
 * Trakero â€” Offline Scan Queue
 *
 * Stores pending scans in IndexedDB when the network is unavailable.
 * Syncs automatically when the connection is restored, both via the
 * browser 'online' event and via the Service Worker Background Sync API.
 *
 * Exposes: window.scanQueue = { add, getCount, refreshBadge, sync }
 */
(function () {
    "use strict";

    var DB_NAME = "qr-reader-queue";
    var STORE_NAME = "scans";
    var DB_VERSION = 1;
    var _db = null;

    /* â”€â”€â”€ IndexedDB helpers â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */

    function openDB() {
        return new Promise(function (resolve, reject) {
            if (_db) {
                resolve(_db);
                return;
            }
            var req = indexedDB.open(DB_NAME, DB_VERSION);
            req.onupgradeneeded = function (e) {
                var db = e.target.result;
                if (!db.objectStoreNames.contains(STORE_NAME)) {
                    db.createObjectStore(STORE_NAME, {
                        keyPath: "id",
                        autoIncrement: true,
                    });
                }
            };
            req.onsuccess = function (e) {
                _db = e.target.result;
                resolve(_db);
            };
            req.onerror = function (e) {
                reject(e.target.error);
            };
        });
    }

    function dbAdd(record) {
        return openDB().then(function (db) {
            return new Promise(function (resolve, reject) {
                var tx = db.transaction(STORE_NAME, "readwrite");
                var req = tx.objectStore(STORE_NAME).add(record);
                req.onsuccess = function () {
                    resolve(req.result);
                };
                req.onerror = function (e) {
                    reject(e.target.error);
                };
            });
        });
    }

    function dbGetAll() {
        return openDB().then(function (db) {
            return new Promise(function (resolve, reject) {
                var tx = db.transaction(STORE_NAME, "readonly");
                var req = tx.objectStore(STORE_NAME).getAll();
                req.onsuccess = function () {
                    resolve(req.result || []);
                };
                req.onerror = function (e) {
                    reject(e.target.error);
                };
            });
        });
    }

    function dbDelete(id) {
        return openDB().then(function (db) {
            return new Promise(function (resolve, reject) {
                var tx = db.transaction(STORE_NAME, "readwrite");
                var req = tx.objectStore(STORE_NAME).delete(id);
                req.onsuccess = function () {
                    resolve();
                };
                req.onerror = function (e) {
                    reject(e.target.error);
                };
            });
        });
    }

    /* â”€â”€â”€ UI badge â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */

    function t(key, fallback) {
        return (typeof translations !== "undefined" && translations[key])
            ? translations[key]
            : fallback;
    }

    function refreshBadge() {
        dbGetAll()
            .then(function (scans) {
                var count = scans.length;
                var badge = document.getElementById("offline-queue-badge");
                var bar   = document.getElementById("offline-queue-bar");
                var txt   = document.getElementById("offline-queue-text");

                if (!badge || !bar) return;

                if (count > 0) {
                    badge.textContent = count;
                    badge.classList.remove("d-none");
                    bar.classList.remove("d-none");
                    if (txt) {
                        txt.textContent = count === 1
                            ? t("offlineQueueOne", "1 scan waiting to sync")
                            : t("offlineQueueMany", "{n} scans waiting to sync").replace("{n}", count);
                    }
                } else {
                    badge.classList.add("d-none");
                    bar.classList.add("d-none");
                }
            })
            .catch(function () {});
    }

    /* â”€â”€â”€ Sync logic â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */

    function postEntry(entry) {
        return fetch(entry.scan_url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": entry.csrf_token,
            },
            body: JSON.stringify(entry.payload),
        }).then(function (response) {
            return response.json().then(function (data) {
                return { ok: response.ok, data: data };
            });
        });
    }

    /**
     * Sends all queued scans to the server in chronological order.
     * Sequential â€” stops if network drops mid-sync.
     * Returns count of successfully synced scans.
     */
    function syncQueue() {
        if (!navigator.onLine) return Promise.resolve(0);

        return dbGetAll().then(function (scans) {
            if (!scans.length) return 0;

            var synced = 0;
            var aborted = false;

            return scans
                .sort(function (a, b) { return a.queued_at - b.queued_at; })
                .reduce(function (chain, entry) {
                    return chain.then(function () {
                        if (aborted) return;

                        return postEntry(entry)
                            .then(function (result) {
                                if (result.ok && result.data.status === "success") {
                                    return dbDelete(entry.id).then(function () {
                                        synced++;
                                    });
                                }
                                // Server returned an error for this scan (e.g. wrong scan sequence).
                                // Remove it to avoid permanent re-queue loop.
                                return dbDelete(entry.id);
                            })
                            .catch(function () {
                                // Network dropped mid-sync â€” stop, leave remaining in queue.
                                aborted = true;
                            });
                    });
                }, Promise.resolve())
                .then(function () {
                    refreshBadge();
                    return synced;
                });
        });
    }

    /* â”€â”€â”€ Add a scan to the offline queue â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */

    function addScan(payload, scanUrl, csrfTokenValue) {
        return dbAdd({
            queued_at: Date.now(),
            payload: payload,
            scan_url: scanUrl,
            csrf_token: csrfTokenValue,
        }).then(function (id) {
            // Register Background Sync (Android Chrome / modern browsers)
            if ("serviceWorker" in navigator && "SyncManager" in window) {
                navigator.serviceWorker.ready
                    .then(function (sw) {
                        return sw.sync.register("qr-scan-sync");
                    })
                    .catch(function () {});
            }
            return id;
        });
    }

    function getCount() {
        return dbGetAll().then(function (s) { return s.length; });
    }

    /* â”€â”€â”€ Auto-sync on reconnect â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */

    window.addEventListener("online", function () {
        syncQueue().then(function (synced) {
            refreshBadge();
            if (synced > 0 && typeof appUI !== "undefined") {
                appUI.fire({
                    icon: "success",
                    title: t("syncComplete", "Synced!"),
                    text: synced + " " + t("synced", "scan(s) uploaded to server"),
                    timer: 2500,
                    showConfirmButton: false,
                });
            }
        });
    });

    // Refresh badge once DOM is ready
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", refreshBadge);
    } else {
        refreshBadge();
    }

    /* â”€â”€â”€ Public API â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */

    window.scanQueue = {
        add: addScan,
        getCount: getCount,
        refreshBadge: refreshBadge,
        sync: syncQueue,
    };
})();

