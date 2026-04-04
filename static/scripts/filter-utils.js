// Filter utilities - shared across all filter pages

// Clear filters function - uses data-clear-url from form
function clearFilters() {
    // Find the active filter form (could be filterForm-main, filterForm-scans, filterForm-vacations)
    const form = document.querySelector('form[id^="filterForm"]');
    if (!form) {
        console.error('Filter form not found');
        return;
    }
    
    const clearUrl = form.getAttribute('data-clear-url');
    if (clearUrl) {
        // Preserve tab parameter if it exists
        const urlParams = new URLSearchParams(window.location.search);
        const tab = urlParams.get('tab');
        if (tab) {
            window.location.href = clearUrl + '?tab=' + tab;
        } else {
            window.location.href = clearUrl;
        }
    }
}

// Auto-submit form on select change
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('form[id^="filterForm"] select').forEach(select => {
        select.addEventListener('change', () => {
            select.closest('form').submit();
        });
    });

    document.querySelectorAll('form[id^="filterForm"] input[type="checkbox"]').forEach(checkbox => {
        checkbox.addEventListener('change', () => {
            checkbox.closest('form').submit();
        });
    });
});
