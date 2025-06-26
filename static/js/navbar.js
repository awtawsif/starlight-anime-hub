// Mobile menu toggle
document.getElementById('menu-toggle').addEventListener('click', function() {
    const navLinks = document.getElementById('nav-links');
    navLinks.classList.toggle('hidden');
    navLinks.classList.toggle('flex');
    if (navLinks.classList.contains('flex')) {
        navLinks.classList.remove('animate-fade-out');
        navLinks.classList.add('animate-fade-in');
    } else {
        navLinks.classList.remove('animate-fade-in');
        navLinks.classList.add('animate-fade-out');
    }
});

// Close mobile menu on larger screens when resized
window.addEventListener('resize', function() {
    const navLinks = document.getElementById('nav-links');
    if (window.innerWidth >= 1024) {
        navLinks.classList.remove('hidden', 'flex', 'animate-fade-in', 'animate-fade-out');
        navLinks.style.display = '';
    } else {
        if (!navLinks.classList.contains('flex')) {
            navLinks.classList.add('hidden');
        }
    }
});

// Hide navbar on scroll down, show on scroll up
let lastScrollTop = 0;
const navbar = document.getElementById('navbar');
const navbarHeight = navbar.offsetHeight;

window.addEventListener('scroll', function() {
    let currentScroll = window.scrollY || document.documentElement.scrollTop;
    if (currentScroll > lastScrollTop && currentScroll > navbarHeight) {
        navbar.classList.add('-translate-y-full', 'opacity-0');
    } else if (currentScroll < lastScrollTop || currentScroll <= 0) {
        navbar.classList.remove('-translate-y-full', 'opacity-0');
    }
    lastScrollTop = currentScroll <= 0 ? 0 : currentScroll;
});
