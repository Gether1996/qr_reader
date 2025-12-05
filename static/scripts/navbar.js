// ============================================
// Navbar Functionality
// Handles desktop dropdowns, mobile menu, and theme toggle
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    // Desktop dropdown functionality
    const desktopDropdowns = document.querySelectorAll('.desktop-navbar .dropdown-trigger');
    desktopDropdowns.forEach(trigger => {
        trigger.addEventListener('click', function(e) {
            e.stopPropagation();
            const parent = this.parentElement;
            const wasActive = parent.classList.contains('active');
            
            // Close all dropdowns
            document.querySelectorAll('.desktop-navbar .dropdown-wrapper').forEach(d => {
                d.classList.remove('active');
            });
            
            // Toggle current
            if (!wasActive) {
                parent.classList.add('active');
            }
        });
    });
    
    // Close desktop dropdowns on outside click
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.desktop-navbar .dropdown-wrapper')) {
            document.querySelectorAll('.desktop-navbar .dropdown-wrapper').forEach(d => {
                d.classList.remove('active');
            });
        }
    });
    
    // Mobile mega menu functionality
    const mobileMegaMenuBtn = document.getElementById('mobileMegaMenuBtn');
    const mobileMegaMenu = document.getElementById('mobileMegaMenu');
    const mobileMegaMenuClose = document.getElementById('mobileMegaMenuClose');
    const body = document.body;
    
    function openMobileMenu() {
        mobileMegaMenu.classList.add('active');
        body.classList.add('mobile-menu-open');
    }
    
    function closeMobileMenu() {
        mobileMegaMenu.classList.remove('active');
        body.classList.remove('mobile-menu-open');
    }
    
    if (mobileMegaMenuBtn) {
        mobileMegaMenuBtn.addEventListener('click', openMobileMenu);
    }
    
    if (mobileMegaMenuClose) {
        mobileMegaMenuClose.addEventListener('click', closeMobileMenu);
    }
    
    // Close on menu item click
    const mobileMenuItems = document.querySelectorAll('.mobile-menu-item');
    mobileMenuItems.forEach(item => {
        item.addEventListener('click', function() {
            setTimeout(closeMobileMenu, 200);
        });
    });
    
    // Close on background click
    if (mobileMegaMenu) {
        mobileMegaMenu.addEventListener('click', function(e) {
            if (e.target === this) {
                closeMobileMenu();
            }
        });
    }
    
    // Theme Toggle Functionality
    const themeToggle = document.getElementById('themeToggle');
    const themeToggleMobile = document.getElementById('themeToggleMobile');
    const themeIconDark = document.getElementById('themeIconDark');
    const themeIconLight = document.getElementById('themeIconLight');
    const themeIconDarkMobile = document.getElementById('themeIconDarkMobile');
    const themeIconLightMobile = document.getElementById('themeIconLightMobile');
    const htmlElement = document.documentElement;
    
    // Get saved theme from localStorage or default to 'light'
    const savedTheme = localStorage.getItem('theme') || 'light';
    
    // Apply saved theme on page load
    function applyTheme(theme) {
        // Set both attributes for compatibility
        htmlElement.setAttribute('data-theme', theme);
        htmlElement.setAttribute('data-bs-theme', theme);
        
        // Force reflow to ensure styles are applied immediately
        void htmlElement.offsetHeight;
        
        // Update mobile menu text
        const themeToggleTitle = document.getElementById('themeToggleTitle');
        const themeToggleSubtitle = document.getElementById('themeToggleSubtitle');
        
        if (theme === 'dark') {
            if (themeIconDark) themeIconDark.style.display = 'none';
            if (themeIconLight) themeIconLight.style.display = 'block';
            if (themeIconDarkMobile) themeIconDarkMobile.style.display = 'none';
            if (themeIconLightMobile) themeIconLightMobile.style.display = 'block';
            if (themeToggleTitle) themeToggleTitle.textContent = themeToggleTitle.getAttribute('data-light-text') || 'Light Mode';
            if (themeToggleSubtitle) themeToggleSubtitle.textContent = themeToggleSubtitle.getAttribute('data-light-text') || 'Switch to light theme';
        } else {
            if (themeIconDark) themeIconDark.style.display = 'block';
            if (themeIconLight) themeIconLight.style.display = 'none';
            if (themeIconDarkMobile) themeIconDarkMobile.style.display = 'block';
            if (themeIconLightMobile) themeIconLightMobile.style.display = 'none';
            if (themeToggleTitle) themeToggleTitle.textContent = themeToggleTitle.getAttribute('data-dark-text') || 'Dark Mode';
            if (themeToggleSubtitle) themeToggleSubtitle.textContent = themeToggleSubtitle.getAttribute('data-dark-text') || 'Switch to dark theme';
        }
    }
    
    // Apply theme immediately
    applyTheme(savedTheme);
    
    // Toggle theme function
    function toggleTheme() {
        const currentTheme = htmlElement.getAttribute('data-bs-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        applyTheme(newTheme);
        localStorage.setItem('theme', newTheme);
    }
    
    // Add event listeners to both desktop and mobile toggle buttons
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
    
    if (themeToggleMobile) {
        themeToggleMobile.addEventListener('click', toggleTheme);
    }
});
