// Magazine Dashboard JavaScript

// Global variables
let currentMagazineId = null;

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    console.log('Magazine Dashboard loaded');
});

// Delete magazine function
function deleteMagazine(magazineId) {
    currentMagazineId = magazineId;
    const modal = new bootstrap.Modal(document.getElementById('deleteMagazineModal'));
    modal.show();
}
