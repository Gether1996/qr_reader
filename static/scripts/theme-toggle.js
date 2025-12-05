// Dark Mode Theme Toggle
document.addEventListener('DOMContentLoaded', function() {
    const themeToggle = document.getElementById('themeToggle');
    
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            
            // Update the theme
            document.documentElement.setAttribute('data-theme', newTheme);
            
            // Save to localStorage
            localStorage.setItem('theme', newTheme);
            
            // If charts exist, update their colors
            if (typeof updateChartsTheme === 'function') {
                updateChartsTheme(newTheme);
            }
        });
    }
});

// Helper function to get current theme
function getCurrentTheme() {
    return document.documentElement.getAttribute('data-theme') || 'light';
}

// Helper function to check if dark mode is active
function isDarkMode() {
    return getCurrentTheme() === 'dark';
}
