/**
 * Roguelike Chronicles — Navigation & Scroll Spy
 * Handles table of contents highlighting and keyboard shortcuts
 */

(function() {
    'use strict';

    const tocLinks = document.querySelectorAll('.toc-link');
    const h2Elements = document.querySelectorAll('.article-content h2[id]');

    /**
     * Update active TOC item based on scroll position
     */
    function updateActiveToc() {
        if (!h2Elements.length || !tocLinks.length) return;

        const scrollPos = window.scrollY + 80;

        let current = null;
        h2Elements.forEach(h2 => {
            const top = h2.offsetTop;
            if (scrollPos >= top) {
                current = h2.id;
            }
        });

        tocLinks.forEach(link => {
            link.classList.remove('active');
            if (link.dataset.target === current) {
                link.classList.add('active');
                // Auto-scroll sidebar to keep active item visible
                link.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'nearest' });
            }
        });
    }

    /**
     * TOC link click — smooth scroll to section
     */
    tocLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const targetId = this.dataset.target;
            const target = document.getElementById(targetId);

            if (target) {
                e.preventDefault();
                const offsetTop = target.offsetTop - 16;
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
                history.pushState(null, null, '#' + targetId);
            }
        });
    });

    /**
     * Scroll spy
     */
    let scrollTimeout;
    window.addEventListener('scroll', function() {
        if (scrollTimeout) return;
        scrollTimeout = setTimeout(() => {
            updateActiveToc();
            scrollTimeout = null;
        }, 50);
    });

    /**
     * Handle initial hash on page load
     */
    function handleHash() {
        const hash = window.location.hash.slice(1);
        if (hash) {
            const target = document.getElementById(hash);
            if (target) {
                setTimeout(() => {
                    const offsetTop = target.offsetTop - 16;
                    window.scrollTo({ top: offsetTop, behavior: 'instant' });
                    updateActiveToc();
                }, 100);
            }
        }
    }
    handleHash();

    /**
     * Keyboard navigation (vim-style)
     */
    document.addEventListener('keydown', function(e) {
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

        switch(e.key) {
            case 'j':
                e.preventDefault();
                window.scrollBy({ top: 40, behavior: 'smooth' });
                break;
            case 'k':
                e.preventDefault();
                window.scrollBy({ top: -40, behavior: 'smooth' });
                break;
            case 'g':
                e.preventDefault();
                if (e.repeat) return;
                // Double-g detection
                if (window._gKeyPressed) {
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                    window._gKeyPressed = false;
                } else {
                    window._gKeyPressed = true;
                    setTimeout(() => { window._gKeyPressed = false; }, 400);
                }
                break;
            case 'G':
                e.preventDefault();
                window.scrollTo({
                    top: document.body.scrollHeight,
                    behavior: 'smooth'
                });
                break;
        }
    });

    /**
     * Mobile sidebar toggle
     */
    if (window.innerWidth <= 768) {
        const sidebar = document.querySelector('.sidebar');
        if (sidebar) {
            // Collapse sidebar sections on mobile (only show header + current game)
            const toc = sidebar.querySelector('.sidebar-toc');
            const otherGames = sidebar.querySelector('.sidebar-other-games');
            const allGames = sidebar.querySelector('.sidebar-all-games');

            // Add toggle buttons for collapsible sections
            [toc, otherGames, allGames].forEach(section => {
                if (!section) return;
                const label = section.querySelector('.toc-label, .other-games-label, .all-games-label');
                const ul = section.querySelector('ul');
                if (label && ul) {
                    label.style.cursor = 'pointer';
                    label.addEventListener('click', () => {
                        ul.style.display = ul.style.display === 'none' ? 'block' : 'none';
                    });
                }
            });
        }
    }

})();
