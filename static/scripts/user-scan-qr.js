// User Scan QR JavaScript Functions

var html5QrcodeScanner = null;
var userLocation = null;
var isScanning = false;
var selectedScanType = null;
var permissionsGranted = false;
var cameraPermission = false;
var locationPermission = false;

// Check if permissions were granted before
function checkExistingPermissions() {
    // Check camera permission
    if (navigator.permissions) {
        navigator.permissions.query({ name: 'camera' }).then(function(result) {
            cameraPermission = result.state === 'granted';
            if (result.state === 'granted') {
                checkLocationPermission();
            }
        }).catch(function() {
            // Permissions API not supported, show permission screen
            showPermissionScreen();
        });
    } else {
        showPermissionScreen();
    }
}

function checkLocationPermission() {
    if (navigator.permissions) {
        navigator.permissions.query({ name: 'geolocation' }).then(function(result) {
            locationPermission = result.state === 'granted';
            if (result.state === 'granted') {
                permissionsGranted = true;
                hidePermissionScreen();
            } else {
                showPermissionScreen();
            }
        }).catch(function() {
            showPermissionScreen();
        });
    } else {
        showPermissionScreen();
    }
}

function showPermissionScreen() {
    document.getElementById('permission-screen').style.display = 'flex';
}

function hidePermissionScreen() {
    document.getElementById('permission-screen').style.display = 'none';
}

// Request all permissions
function requestPermissions() {
    return new Promise(function(resolve, reject) {
        // First request location
        if (!navigator.geolocation) {
            reject(new Error(translations.geolocationNotSupported || 'Geolocation not supported'));
            return;
        }

        navigator.geolocation.getCurrentPosition(
            function(position) {
                userLocation = {
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude
                };
                locationPermission = true;
                console.log('Location permission granted:', userLocation);
                
                // Then try camera
                if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
                    navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } })
                        .then(function(stream) {
                            // Stop the stream immediately, we just needed permission
                            stream.getTracks().forEach(function(track) { track.stop(); });
                            cameraPermission = true;
                            permissionsGranted = true;
                            console.log('Camera permission granted');
                            resolve();
                        })
                        .catch(function(err) {
                            reject(new Error(translations.cameraPermissionDenied || 'Camera permission denied'));
                        });
                } else {
                    reject(new Error(translations.cameraNotSupported || 'Camera not supported'));
                }
            },
            function(error) {
                console.error('Location error:', error);
                var errorMsg = translations.unableToGetLocation || 'Unable to get location';
                switch(error.code) {
                    case error.PERMISSION_DENIED:
                        errorMsg = translations.allowLocationAccess || 'Please allow location access';
                        break;
                    case error.POSITION_UNAVAILABLE:
                        errorMsg = translations.locationUnavailable || 'Location unavailable';
                        break;
                    case error.TIMEOUT:
                        errorMsg = translations.locationTimeout || 'Location request timeout';
                        break;
                }
                reject(new Error(errorMsg));
            },
            {
                enableHighAccuracy: true,
                timeout: 15000,
                maximumAge: 0
            }
        );
    });
}

function initGrantPermissionButton() {
    document.getElementById('grant-permission-btn').addEventListener('click', function() {
        var btn = this;
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>' + (translations.requesting || 'Requesting permissions...');
        
        requestPermissions()
            .then(function() {
                hidePermissionScreen();
                Swal.fire({
                    icon: 'success',
                    title: translations.permissionsGranted || 'Permissions Granted',
                    text: translations.canNowScan || 'You can now scan QR codes',
                    timer: 2000,
                    showConfirmButton: false
                });
            })
            .catch(function(error) {
                btn.disabled = false;
                btn.innerHTML = '<i class="fas fa-shield-alt me-2"></i>' + (translations.grantPermissions || 'Grant Permissions');
                
                Swal.fire({
                    icon: 'error',
                    title: translations.permissionError || 'Permission Error',
                    text: error.message,
                    confirmButtonText: translations.tryAgain || 'Try Again'
                });
            });
    });
}

function initScanTypeButtons() {
    var scanTypeButtons = document.querySelectorAll('.scan-type-btn-mobile');
    scanTypeButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            if (!permissionsGranted) {
                showPermissionScreen();
                return;
            }
            
            // Remove active class from all buttons
            scanTypeButtons.forEach(function(btn) {
                btn.classList.remove('active');
            });
            
            // Add active class to clicked button
            this.classList.add('active');
            
            // Store selected scan type
            selectedScanType = this.getAttribute('data-type');
            
            // Hide warning
            document.getElementById('scan-type-warning').style.display = 'none';
            
            // Show start button
            var startBtn = document.getElementById('startScanBtn');
            startBtn.style.display = 'flex';
            startBtn.disabled = false;
            startBtn.innerHTML = '<i class="fas fa-camera"></i><span>' + (translations.startScanner || 'Start Scanner') + '</span>';
            
            console.log('Scan type selected:', selectedScanType);
        });
    });
}

function stopScanner() {
    if (html5QrcodeScanner && isScanning) {
        html5QrcodeScanner.stop().then(function() {
            console.log('Scanner stopped successfully');
            isScanning = false;
            html5QrcodeScanner = null;
            document.getElementById('camera-container').style.display = 'none';
            document.getElementById('stopScanBtn').style.display = 'none';
            document.getElementById('startScanBtn').style.display = 'flex';
        }).catch(function(err) {
            console.error('Error stopping scanner:', err);
            isScanning = false;
            html5QrcodeScanner = null;
        });
    }
}

function processScan(uuid, scanUrl) {
    if (isScanning) {
        stopScanner();
    }
    submitScan(uuid, scanUrl);
}

function submitScan(uuid, scanUrl) {
    if (!selectedScanType) {
        document.getElementById('scan-type-warning').style.display = 'block';
        return;
    }
    
    if (!userLocation) {
        Swal.fire({
            icon: 'error',
            title: translations.locationRequired || 'Location Required',
            text: translations.pleaseEnableLocation || 'Please enable location'
        });
        return;
    }
    
    var loadingOverlay = document.getElementById('loading-overlay');
    loadingOverlay.style.display = 'flex';
    loadingOverlay.querySelector('.text-white').innerHTML = '<i class="fas fa-sync fa-spin me-2"></i>' + (translations.processingScan || 'Processing scan...');
    
    var extractedUuid = uuid.trim();
    if (extractedUuid.includes('/scan/')) {
        var parts = extractedUuid.split('/scan/');
        if (parts.length > 1) {
            extractedUuid = parts[1].replace(/\//g, '');
        }
    }

    fetch(scanUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
            uuid: extractedUuid,
            latitude: userLocation.latitude,
            longitude: userLocation.longitude,
            scan_type: selectedScanType
        })
    })
    .then(function(response) { return response.json(); })
    .then(function(data) {
        document.getElementById('loading-overlay').style.display = 'none';
        
        if (data.status === 'success') {
            Swal.fire({
                icon: 'success',
                title: translations.scanSuccessful || 'Scan Successful',
                text: data.data.qr_name + ' - ' + data.data.qr_location,
                timer: 1500,
                showConfirmButton: false,
                allowOutsideClick: false
            }).then(function() {
                const langCode = window.location.pathname.split('/')[1];
                window.location.href = `/${langCode}/user/dashboard/`;
            });
        } else {
            Swal.fire({
                icon: 'error',
                title: translations.scanFailed || 'Scan Failed',
                text: data.message,
                confirmButtonText: translations.tryAgain || 'Try Again'
            });
        }
    })
    .catch(function(error) {
        document.getElementById('loading-overlay').style.display = 'none';
        console.error('Scan processing error:', error);
        Swal.fire({
            icon: 'error',
            title: translations.error || 'Error',
            text: error.message
        });
    });
}

function startScanner() {
    var cameraContainer = document.getElementById('camera-container');
    var startBtn = document.getElementById('startScanBtn');
    var stopBtn = document.getElementById('stopScanBtn');

    // Show loading overlay
    document.getElementById('loading-overlay').style.display = 'flex';
    document.getElementById('loading-overlay').querySelector('.text-white').innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>' + (translations.initializingScanner || 'Initializing scanner...');

    html5QrcodeScanner = new Html5Qrcode("qr-reader");
    
    html5QrcodeScanner.start(
        { facingMode: "environment" },
        {
            fps: 10,
            qrbox: { width: 250, height: 250 },
            aspectRatio: 1.0
        },
        function(decodedText) {
            console.log('QR Code detected:', decodedText);
            const langCode = window.location.pathname.split('/')[1];
            const scanUrl = `/${langCode}/user/scan/`;
            processScan(decodedText, scanUrl);
        },
        function(errorMessage) {
            // Ignore scan errors (they happen every frame)
        }
    ).then(function() {
        isScanning = true;
        console.log('Scanner started successfully');
        
        // Hide loading and show scanner
        document.getElementById('loading-overlay').style.display = 'none';
        cameraContainer.style.display = 'flex';
        startBtn.style.display = 'none';
        stopBtn.style.display = 'flex';
    }).catch(function(err) {
        console.error('Scanner initialization error:', err);
        document.getElementById('loading-overlay').style.display = 'none';
        
        Swal.fire({
            icon: 'error',
            title: translations.scannerError || 'Scanner Error',
            text: err.message || (translations.failedToStart || 'Failed to start scanner')
        });
        
        cameraContainer.style.display = 'none';
        startBtn.style.display = 'flex';
        startBtn.disabled = false;
        stopBtn.style.display = 'none';
    });
}

function initStartScanButton() {
    document.getElementById('startScanBtn').addEventListener('click', function() {
        var btn = this;
        
        if (!permissionsGranted) {
            showPermissionScreen();
            return;
        }
        
        if (!selectedScanType) {
            document.getElementById('scan-type-warning').style.display = 'block';
            return;
        }
        
        // Disable button and show loading state
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i><span>' + (translations.preparing || 'Preparing...') + '</span>';
        
        // Re-check and get fresh location before starting scanner
        if (!userLocation) {
            navigator.geolocation.getCurrentPosition(
                function(position) {
                    userLocation = {
                        latitude: position.coords.latitude,
                        longitude: position.coords.longitude
                    };
                    console.log('Location refreshed:', userLocation);
                    startScanner();
                },
                function(error) {
                    console.error('Location error:', error);
                    
                    // Re-enable button
                    btn.disabled = false;
                    btn.innerHTML = '<i class="fas fa-camera"></i><span>' + (translations.startScanner || 'Start Scanner') + '</span>';
                    
                    Swal.fire({
                        icon: 'error',
                        title: translations.locationRequired || 'Location Required',
                        text: translations.allowLocationAccess || 'Please allow location access in your browser settings',
                        confirmButtonText: 'OK'
                    });
                },
                {
                    enableHighAccuracy: true,
                    timeout: 15000,
                    maximumAge: 0
                }
            );
        } else {
            startScanner();
        }
    });
}

function initStopScanButton() {
    document.getElementById('stopScanBtn').addEventListener('click', function() {
        stopScanner();
    });
}

// Initialize everything
function initUserScanQR() {
    initGrantPermissionButton();
    initScanTypeButtons();
    initStartScanButton();
    initStopScanButton();
    
    // Check permissions on page load
    checkExistingPermissions();
    
    // Cleanup on page unload
    window.addEventListener('beforeunload', function() {
        if (isScanning) {
            stopScanner();
        }
    });
}

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initUserScanQR);
} else {
    initUserScanQR();
}
