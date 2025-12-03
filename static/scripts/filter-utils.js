// Filter utilities - shared across all filter pages

// Clear filters function - uses data-clear-url from form
function clearFilters() {
    const form = document.getElementById('filterForm');
    const clearUrl = form.getAttribute('data-clear-url');
    if (clearUrl) {
        window.location.href = clearUrl;
    }
}

// Auto-submit form on select change
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('#filterForm select').forEach(select => {
        select.addEventListener('change', () => {
            document.getElementById('filterForm').submit();
        });
    });
});
