/**
 * Roguelike Chronicles — Navigation & Scroll Spy
 * Handles table of contents highlighting and keyboard shortcuts
 */

(function() {
    'use strict';

    const tocLinks = document.querySelectorAll('.toc-link');
    const h2Elements = document.querySelectorAll('.article-content h2[id]');
    const sidebar = document.querySelector('.sidebar');
    const desktopSidebar = window.matchMedia('(min-width: 769px)');

    /**
     * Прокрутить пункт TOC только внутри сайдбара (не трогать window).
     * scrollIntoView() на мобилке тянет страницу к сайдбару вверху — отсюда «откат».
     */
    function scrollTocLinkInSidebar(link) {
        if (!sidebar || !desktopSidebar.matches) return;
        if (sidebar.scrollHeight <= sidebar.clientHeight) return;

        const linkRect = link.getBoundingClientRect();
        const sidebarRect = sidebar.getBoundingClientRect();

        if (linkRect.top < sidebarRect.top) {
            sidebar.scrollTop += linkRect.top - sidebarRect.top - 8;
        } else if (linkRect.bottom > sidebarRect.bottom) {
            sidebar.scrollTop += linkRect.bottom - sidebarRect.bottom + 8;
        }
    }

    /**
     * Update active TOC item based on scroll position
     */
    function updateActiveToc() {
        if (!h2Elements.length || !tocLinks.length) return;

        const scrollPos = window.scrollY + 80;

        let current = null;
        h2Elements.forEach(h2 => {
            const top = h2.getBoundingClientRect().top + window.scrollY;
            if (scrollPos >= top) {
                current = h2.id;
            }
        });

        tocLinks.forEach(link => {
            link.classList.remove('active');
            if (link.dataset.target === current) {
                link.classList.add('active');
                scrollTocLinkInSidebar(link);
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
                const top = target.getBoundingClientRect().top + window.scrollY - 16;
                window.scrollTo({
                    top: top,
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
    }, { passive: true });

    /**
     * Handle initial hash on page load
     */
    function handleHash() {
        const hash = window.location.hash.slice(1);
        if (hash) {
            const target = document.getElementById(hash);
            if (target) {
                setTimeout(() => {
                    const top = target.getBoundingClientRect().top + window.scrollY - 16;
                    window.scrollTo({ top: top, behavior: 'instant' });
                    updateActiveToc();
                }, 100);
            }
        }
    }
    handleHash();

    /**
     * Keyboard navigation (vim-style) — только не на сенсорных устройствах без клавиатуры
     */
    if (!window.matchMedia('(hover: none) and (pointer: coarse)').matches) {
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
    }

    /**
     * Mobile sidebar — сворачивание секций по тапу на заголовок
     */
    if (window.innerWidth <= 768) {
        if (sidebar) {
            const toc = sidebar.querySelector('.sidebar-toc');
            const otherGames = sidebar.querySelector('.sidebar-other-games');
            const allGames = sidebar.querySelector('.sidebar-all-games');

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

    /**
     * Image modal — открытие по клику, закрытие по клику на изображение или фон
     */
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    const modalImg = document.createElement('img');
    modal.appendChild(modalImg);
    document.body.appendChild(modal);

    document.addEventListener('click', function(e) {
        const target = e.target.closest('.article-content img');
        if (!target) return;
        modalImg.src = target.src;
        modalImg.alt = target.alt;
        modal.classList.add('open');
    });

    modal.addEventListener('click', function() {
        modal.classList.remove('open');
    });

})();
