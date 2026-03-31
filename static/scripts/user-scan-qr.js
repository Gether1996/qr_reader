var html5QrcodeScanner = null;
var userLocation = null;
var userLocationTimestamp = 0;
var isScannerActive = false;
var isStartingScanner = false;
var isSubmitting = false;
var selectedScanType = null;
var permissionsGranted = false;
var cameraPermission = false;
var locationPermission = false;

var LOCATION_FRESH_MS = 60 * 1000;

function getLangCode() {
    var pathPart = window.location.pathname.split("/")[1];
    return pathPart || "sk";
}
function getScanUrl() {
    return "/" + getLangCode() + "/user/scan/";
}

function getText(key, fallback) {
    if (typeof translations !== "undefined" && translations[key]) {
        return translations[key];
    }
    return fallback;
}

function getScanTypeLabel(scanType) {
    var mapping = {
        arrival: getText("arrival", "Arrival"),
        departure: getText("departure", "Departure"),
        lunch_break_start: getText("lunchBreakStart", "Lunch break start"),
        lunch_break_end: getText("lunchBreakEnd", "Lunch break end"),
    };
    return mapping[scanType] || scanType;
}

function getActionButtons() {
    return {
        start: document.getElementById("startScanBtn"),
        homeOffice: document.getElementById("homeOfficeBtn"),
        businessTrip: document.getElementById("businessTripBtn"),
        noQr: document.getElementById("noQrBtn"),
        stop: document.getElementById("stopScanBtn"),
    };
}

function getScanTypeButtons() {
    return Array.from(document.querySelectorAll(".scan-type-btn-mobile"));
}

function isInteractionLocked() {
    return isSubmitting || isStartingScanner;
}

function showLoading(message) {
    var overlay = document.getElementById("loading-overlay");
    var text = overlay.querySelector(".loading-text");

    overlay.classList.remove("d-none");
    overlay.classList.add("d-flex");
    text.innerHTML = '<i class="fas fa-sync fa-spin me-2"></i>' + message;
}

function hideLoading() {
    var overlay = document.getElementById("loading-overlay");
    overlay.classList.remove("d-flex");
    overlay.classList.add("d-none");
}

function showPermissionScreen() {
    var screen = document.getElementById("permission-screen");
    screen.classList.remove("d-none");
    screen.classList.add("d-flex");
}

function hidePermissionScreen() {
    var screen = document.getElementById("permission-screen");
    screen.classList.remove("d-flex");
    screen.classList.add("d-none");
}

function setActionButtonsVisibility(show) {
    var container = document.getElementById("action-buttons-container");
    container.classList.toggle("d-none", !show);
    container.classList.toggle("d-flex", show);
}

function setCameraVisibility(show) {
    var cameraContainer = document.getElementById("camera-container");
    cameraContainer.classList.toggle("d-none", !show);
    cameraContainer.classList.toggle("d-flex", show);
}

function setStopButtonVisibility(show) {
    var stopBtn = document.getElementById("stopScanBtn");
    stopBtn.classList.toggle("d-none", !show);
    stopBtn.classList.toggle("d-flex", show);
}

function setControlsDisabled(disabled) {
    getScanTypeButtons().forEach(function(button) {
        if (!button.dataset.serverDisabled) {
            button.disabled = disabled;
        }
    });

    var buttons = getActionButtons();
    buttons.start.disabled = disabled;
    buttons.homeOffice.disabled = disabled;
    buttons.businessTrip.disabled = disabled;
    buttons.noQr.disabled = disabled;
    buttons.stop.disabled = disabled;
}

function setStartButtonLabel() {
    var startBtn = document.getElementById("startScanBtn");
    var label = selectedScanType
        ? getText("scanWorkplaceQr", "Scan Workplace QR")
        : getText("startScanner", "Start Scanner");

    startBtn.innerHTML = '<i class="fas fa-camera"></i><span>' + label + "</span>";
}

function updateStatusPanel() {
    // Status panel elements were removed from the UI
}

function updateActionArea() {
    var shouldShowActions = !!selectedScanType && !isScannerActive;
    setActionButtonsVisibility(shouldShowActions);
    setStopButtonVisibility(isScannerActive);
    setStartButtonLabel();
    updateStatusPanel();
}

function storeLocation(position) {
    userLocation = {
        latitude: position.coords.latitude,
        longitude: position.coords.longitude,
    };
    userLocationTimestamp = Date.now();
    locationPermission = true;
    permissionsGranted = cameraPermission && locationPermission;
    updateStatusPanel();
}

function ensureFreshLocation(forceRefresh) {
    return new Promise(function(resolve, reject) {
        if (!navigator.geolocation) {
            reject(new Error(getText("geolocationNotSupported", "Geolocation not supported")));
            return;
        }

        if (
            !forceRefresh &&
            userLocation &&
            userLocationTimestamp &&
            Date.now() - userLocationTimestamp < LOCATION_FRESH_MS
        ) {
            resolve(userLocation);
            return;
        }

        navigator.geolocation.getCurrentPosition(
            function(position) {
                storeLocation(position);
                resolve(userLocation);
            },
            function(error) {
                var errorMsg = getText("unableToGetLocation", "Unable to get your location.");

                if (error.code === error.PERMISSION_DENIED) {
                    locationPermission = false;
                    permissionsGranted = false;
                    errorMsg = getText(
                        "allowLocationAccess",
                        "Please allow location access in your browser settings."
                    );
                } else if (error.code === error.POSITION_UNAVAILABLE) {
                    errorMsg = getText("locationUnavailable", "Location information is unavailable.");
                } else if (error.code === error.TIMEOUT) {
                    errorMsg = getText("locationTimeout", "Location request timed out.");
                }

                updateStatusPanel();
                reject(new Error(errorMsg));
            },
            {
                enableHighAccuracy: true,
                timeout: 15000,
                maximumAge: 0,
            }
        );
    });
}

function queryPermissionState(name) {
    if (!navigator.permissions || !navigator.permissions.query) {
        return Promise.resolve(null);
    }

    return navigator.permissions
        .query({ name: name })
        .then(function(result) {
            return result.state;
        })
        .catch(function() {
            return null;
        });
}

function requestPermissions() {
    return new Promise(function(resolve, reject) {
        ensureFreshLocation(true)
            .then(function() {
                if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                    throw new Error(getText("cameraNotSupported", "Camera not supported"));
                }

                return navigator.mediaDevices.getUserMedia({
                    video: {
                        facingMode: "environment",
                    },
                });
            })
            .then(function(stream) {
                stream.getTracks().forEach(function(track) {
                    track.stop();
                });

                cameraPermission = true;
                permissionsGranted = cameraPermission && locationPermission;
                hidePermissionScreen();
                updateStatusPanel();
                resolve();
            })
            .catch(function(error) {
                cameraPermission = false;
                permissionsGranted = false;
                updateStatusPanel();
                reject(
                    error instanceof Error
                        ? error
                        : new Error(getText("cameraPermissionDenied", "Camera permission denied"))
                );
            });
    });
}

function checkExistingPermissions() {
    Promise.all([
        queryPermissionState("geolocation"),
        queryPermissionState("camera"),
    ])
        .then(function(states) {
            locationPermission = states[0] === "granted";
            cameraPermission = states[1] === "granted";
            permissionsGranted = cameraPermission && locationPermission;

            if (locationPermission) {
                return ensureFreshLocation(false).catch(function() {
                    return null;
                });
            }

            return null;
        })
        .finally(function() {
            hidePermissionScreen();
            updateStatusPanel();
        });
}

function stopScanner(options) {
    var config = options || {};

    function finalizeStop() {
        isScannerActive = false;
        isStartingScanner = false;
        html5QrcodeScanner = null;
        setCameraVisibility(false);
        setStopButtonVisibility(false);

        if (config.restoreActions !== false) {
            setControlsDisabled(false);
            updateActionArea();
        } else {
            updateStatusPanel();
        }
    }

    if (!html5QrcodeScanner || !isScannerActive) {
        finalizeStop();
        return Promise.resolve();
    }

    return html5QrcodeScanner
        .stop()
        .catch(function() {
            return null;
        })
        .then(function() {
            if (html5QrcodeScanner && html5QrcodeScanner.clear) {
                return html5QrcodeScanner.clear().catch(function() {
                    return null;
                });
            }

            return null;
        })
        .finally(finalizeStop);
}

function showErrorAlert(title, text) {
    return appUI.fire({
        icon: "error",
        title: title,
        text: text,
        customClass: {
            confirmButton: "swal-btn-gradient-red",
            popup: "swal-popup-rounded",
        },
        buttonsStyling: false,
    });
}

function showSuccessAlert(title, text) {
    return appUI.fire({
        icon: "success",
        title: title,
        text: text,
        timer: 1400,
        showConfirmButton: false,
        allowOutsideClick: false,
        customClass: {
            popup: "swal-popup-rounded",
        },
    });
}

function beginBusyState(message) {
    if (isSubmitting || isStartingScanner) {
        return false;
    }

    isSubmitting = true;
    setControlsDisabled(true);
    updateStatusPanel();
    showLoading(message);
    return true;
}

function resetIdleState() {
    hideLoading();
    isSubmitting = false;
    setControlsDisabled(false);
    updateActionArea();
}

function submitScan(payload, options) {
    var config = options || {};
    var requestLocked = config.alreadyLocked === true;

    if (!requestLocked && !beginBusyState(getText("processingScan", "Processing scan..."))) {
        return Promise.resolve();
    }

    return fetch(getScanUrl(), {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify(payload),
    })
        .then(function(response) {
            return response
                .json()
                .catch(function() {
                    return {
                        status: "error",
                        message: getText("unknownError", "An unknown error occurred."),
                    };
                })
                .then(function(data) {
                    return {
                        ok: response.ok,
                        data: data,
                    };
                });
        })
        .then(function(result) {
            if (result.ok && result.data.status === "success") {
                hideLoading();

                var successMessage = result.data.data.qr_name;
                if (result.data.data.qr_location) {
                    successMessage += " - " + result.data.data.qr_location;
                }

                return showSuccessAlert(
                    getText("scanSuccessful", "Scan Successful!"),
                    successMessage
                ).then(function() {
                    window.location.href = "/" + getLangCode() + "/user/dashboard/";
                });
            }

            resetIdleState();
            return showErrorAlert(
                getText("scanFailed", "Scan Failed"),
                result.data.message || getText("failedToRecord", "Failed to record scan")
            );
        })
        .catch(function(error) {
            resetIdleState();
            return showErrorAlert(
                getText("error", "Error!"),
                error.message || getText("failedToProcess", "Failed to process scan")
            );
        });
}

function normalizeDecodedQrValue(decodedText) {
    var extractedUuid = (decodedText || "").trim();

    if (extractedUuid.includes("/scan/")) {
        var parts = extractedUuid.split("/scan/");
        if (parts.length > 1) {
            extractedUuid = parts[1].replace(/\//g, "");
        }
    }

    return extractedUuid;
}

function handleInteractionFailure(title, error) {
    resetIdleState();

    if (
        error &&
        error.message &&
        error.message === getText(
            "allowLocationAccess",
            "Please allow location access in your browser settings."
        )
    ) {
        showPermissionScreen();
    }

    return showErrorAlert(title, error.message);
}

function processScan(decodedText) {
    if (isInteractionLocked() || isScannerActive === false) {
        return;
    }

    var extractedUuid = normalizeDecodedQrValue(decodedText);
    if (!extractedUuid) {
        return showErrorAlert(
            getText("uuidRequired", "UUID Required"),
            getText("pleaseEnterUuid", "Please enter a QR code UUID")
        );
    }

    if (!beginBusyState(getText("processingScan", "Processing scan..."))) {
        return;
    }

    stopScanner({ restoreActions: false })
        .then(function() {
            return ensureFreshLocation(true);
        })
        .then(function(location) {
            return submitScan(
                {
                    uuid: extractedUuid,
                    latitude: location.latitude,
                    longitude: location.longitude,
                    scan_type: selectedScanType,
                    is_home_office: false,
                    is_business_trip: false,
                    is_no_qr: false,
                },
                { alreadyLocked: true }
            );
        })
        .catch(function(error) {
            return handleInteractionFailure(
                getText("locationRequired", "Location Required"),
                error
            );
        });
}

function startHtml5Scanner(cameraConfig) {
    return html5QrcodeScanner.start(
        cameraConfig,
        {
            fps: 10,
            qrbox: function(viewfinderWidth, viewfinderHeight) {
                var edge = Math.min(viewfinderWidth, viewfinderHeight, 300);
                return {
                    width: edge,
                    height: edge,
                };
            },
            aspectRatio: 1.0,
        },
        function(decodedText) {
            processScan(decodedText);
        },
        function() {
            return null;
        }
    );
}

function startScanner() {
    if (!selectedScanType || isInteractionLocked() || isScannerActive) {
        return;
    }

    isStartingScanner = true;
    setControlsDisabled(true);
    updateStatusPanel();
    showLoading(getText("initializingScanner", "Initializing scanner..."));

    html5QrcodeScanner = new Html5Qrcode("qr-reader");

    startHtml5Scanner({ facingMode: "environment" })
        .catch(function() {
            return Html5Qrcode.getCameras().then(function(cameras) {
                if (!cameras || !cameras.length) {
                    throw new Error(getText("cameraNotSupported", "Camera not supported"));
                }

                return startHtml5Scanner(cameras[0].id);
            });
        })
        .then(function() {
            hideLoading();
            isStartingScanner = false;
            isScannerActive = true;
            setCameraVisibility(true);
            setActionButtonsVisibility(false);
            setStopButtonVisibility(true);
            setControlsDisabled(false);
            updateStatusPanel();
        })
        .catch(function(error) {
            hideLoading();
            isStartingScanner = false;
            setControlsDisabled(false);
            updateActionArea();
            showErrorAlert(
                getText("scannerError", "Scanner Error"),
                error.message || getText("failedToStart", "Failed to start scanner")
            );
        });
}

function initGrantPermissionButton() {
    document.getElementById("grant-permission-btn").addEventListener("click", function() {
        var button = this;

        button.disabled = true;
        button.innerHTML =
            '<i class="fas fa-spinner fa-spin me-2"></i>' +
            getText("requesting", "Requesting permissions...");

        requestPermissions()
            .then(function() {
                button.disabled = false;
                button.innerHTML =
                    '<i class="fas fa-shield-alt me-2"></i>' +
                    getText("grantPermissions", "Grant Permissions");

                return appUI.fire({
                    icon: "success",
                    title: getText("permissionsGranted", "Permissions Granted"),
                    text: getText("canNowScan", "You can now scan QR codes"),
                    timer: 1800,
                    showConfirmButton: false,
                    customClass: {
                        popup: "swal-popup-rounded",
                    },
                });
            })
            .catch(function(error) {
                button.disabled = false;
                button.innerHTML =
                    '<i class="fas fa-shield-alt me-2"></i>' +
                    getText("grantPermissions", "Grant Permissions");

                return showErrorAlert(
                    getText("permissionError", "Permission Error"),
                    error.message
                );
            });
    });
}

function initScanTypeButtons() {
    getScanTypeButtons().forEach(function(button) {
        if (button.disabled) {
            button.dataset.serverDisabled = "true";
        }

        button.addEventListener("click", function() {
            if (this.disabled || isInteractionLocked() || isScannerActive) {
                return;
            }

            getScanTypeButtons().forEach(function(btn) {
                btn.classList.remove("active");
            });

            this.classList.add("active");
            selectedScanType = this.getAttribute("data-type");
            document.getElementById("scan-type-warning").classList.add("d-none");
            updateActionArea();
        });
    });
}

function runManualScan(mode) {
    if (isInteractionLocked() || isScannerActive) {
        return;
    }

    if (!selectedScanType) {
        document.getElementById("scan-type-warning").classList.remove("d-none");
        return;
    }

    if (!permissionsGranted) {
        showPermissionScreen();
        updateStatusPanel();
        return;
    }

    if (!beginBusyState(getText("preparing", "Preparing..."))) {
        return;
    }

    ensureFreshLocation(true)
        .then(function(location) {
            var isHomeOffice = mode === "home_office";
            var isBusinessTrip = mode === "business_trip";
            var isNoQr = mode === "no_qr";

            return submitScan(
                {
                    latitude: location.latitude,
                    longitude: location.longitude,
                    scan_type: selectedScanType,
                    is_home_office: isHomeOffice,
                    is_business_trip: isBusinessTrip,
                    is_no_qr: isNoQr,
                },
                { alreadyLocked: true }
            );
        })
        .catch(function(error) {
            return handleInteractionFailure(
                getText("locationRequired", "Location Required"),
                error
            );
        });
}

function initStartScanButton() {
    document.getElementById("startScanBtn").addEventListener("click", function() {
        if (isInteractionLocked() || isScannerActive) {
            return;
        }

        if (!selectedScanType) {
            document.getElementById("scan-type-warning").classList.remove("d-none");
            return;
        }

        if (!permissionsGranted) {
            showPermissionScreen();
            updateStatusPanel();
            return;
        }

        ensureFreshLocation(false)
            .then(function() {
                startScanner();
            })
            .catch(function(error) {
                showPermissionScreen();
                showErrorAlert(
                    getText("locationRequired", "Location Required"),
                    error.message
                );
            });
    });
}

function initStopScanButton() {
    document.getElementById("stopScanBtn").addEventListener("click", function() {
        if (isSubmitting) {
            return;
        }

        setControlsDisabled(true);
        stopScanner({ restoreActions: true });
    });
}

function initHomeOfficeButton() {
    document.getElementById("homeOfficeBtn").addEventListener("click", function() {
        if (isInteractionLocked() || isScannerActive) {
            return;
        }

        if (!selectedScanType) {
            document.getElementById("scan-type-warning").classList.remove("d-none");
            return;
        }

        appUI.fire({
            title: getText("confirmHomeOffice", "Confirm Home Office"),
            text: getText(
                "confirmHomeOfficeText",
                "Are you sure you want to scan from home office?"
            ),
            icon: "question",
            showCancelButton: true,
            confirmButtonText: getText("yes", "Yes"),
            cancelButtonText: getText("no", "No"),
            customClass: {
                confirmButton: "swal-btn-gradient-green",
                cancelButton: "swal-btn-gradient-red",
                popup: "swal-popup-rounded",
            },
            buttonsStyling: false,
        }).then(function(result) {
            if (result.isConfirmed) {
                runManualScan("home_office");
            }
        });
    });
}

function initBusinessTripButton() {
    document.getElementById("businessTripBtn").addEventListener("click", function() {
        if (isInteractionLocked() || isScannerActive) {
            return;
        }

        if (!selectedScanType) {
            document.getElementById("scan-type-warning").classList.remove("d-none");
            return;
        }

        appUI.fire({
            title: getText("confirmBusinessTrip", "Confirm Business Trip"),
            text: getText(
                "confirmBusinessTripText",
                "Are you sure you want to scan from business trip?"
            ),
            icon: "question",
            showCancelButton: true,
            confirmButtonText: getText("yes", "Yes"),
            cancelButtonText: getText("no", "No"),
            customClass: {
                confirmButton: "swal-btn-gradient-green",
                cancelButton: "swal-btn-gradient-red",
                popup: "swal-popup-rounded",
            },
            buttonsStyling: false,
        }).then(function(result) {
            if (result.isConfirmed) {
                runManualScan("business_trip");
            }
        });
    });
}

function initNoQrButton() {
    document.getElementById("noQrBtn").addEventListener("click", function() {
        if (isInteractionLocked() || isScannerActive) {
            return;
        }

        if (!selectedScanType) {
            document.getElementById("scan-type-warning").classList.remove("d-none");
            return;
        }

        appUI.fire({
            title: getText("confirmNoQr", "Confirm No QR"),
            text: getText(
                "confirmNoQrText",
                "Are you sure you want to record a scan without a QR code?"
            ),
            icon: "question",
            showCancelButton: true,
            confirmButtonText: getText("yes", "Yes"),
            cancelButtonText: getText("no", "No"),
            customClass: {
                confirmButton: "swal-btn-gradient-green",
                cancelButton: "swal-btn-gradient-red",
                popup: "swal-popup-rounded",
            },
            buttonsStyling: false,
        }).then(function(result) {
            if (result.isConfirmed) {
                runManualScan("no_qr");
            }
        });
    });
}

function initLifecycleHandlers() {
    document.addEventListener("visibilitychange", function() {
        if (!document.hidden) {
            checkExistingPermissions();
        }
    });

    window.addEventListener("beforeunload", function() {
        if (isScannerActive) {
            stopScanner({ restoreActions: false });
        }
    });
}

function initUserScanQR() {
    initGrantPermissionButton();
    initScanTypeButtons();
    initStartScanButton();
    initStopScanButton();
    initHomeOfficeButton();
    initBusinessTripButton();
    initNoQrButton();
    initLifecycleHandlers();
    checkExistingPermissions();
    updateActionArea();
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initUserScanQR);
} else {
    initUserScanQR();
}
