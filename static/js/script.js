document.addEventListener('DOMContentLoaded', () => {

    /* =========================================================
       MOBILE NAVIGATION
       ========================================================= */

    const navToggle = document.getElementById('navToggle');
    const navLinks = document.getElementById('navLinks');

    function closeMobileNav() {
        if (!navToggle || !navLinks) return;

        navLinks.classList.remove('open');

        navToggle.setAttribute(
            'aria-expanded',
            'false'
        );

        navToggle.setAttribute(
            'aria-label',
            'Open navigation menu'
        );
    }

    if (navToggle && navLinks) {

        navToggle.setAttribute(
            'aria-expanded',
            'false'
        );

        navToggle.addEventListener('click', event => {

            event.stopPropagation();

            navLinks.classList.toggle('open');

            const isOpen =
                navLinks.classList.contains('open');

            navToggle.setAttribute(
                'aria-expanded',
                isOpen ? 'true' : 'false'
            );

            navToggle.setAttribute(
                'aria-label',
                isOpen
                    ? 'Close navigation menu'
                    : 'Open navigation menu'
            );

        });

        navLinks.querySelectorAll('a').forEach(link => {

            link.addEventListener('click', () => {
                closeMobileNav();
            });

        });

    }


    /* =========================================================
       CLOSE MOBILE NAV WHEN CLICKING OUTSIDE
       ========================================================= */

    document.addEventListener('click', event => {

        if (!navToggle || !navLinks) return;

        const clickedInsideNav =
            navLinks.contains(event.target);

        const clickedToggle =
            navToggle.contains(event.target);

        if (
            navLinks.classList.contains('open') &&
            !clickedInsideNav &&
            !clickedToggle
        ) {
            closeMobileNav();
        }

    });


    /* =========================================================
       ESCAPE KEY
       ========================================================= */

    document.addEventListener('keydown', event => {

        if (event.key === 'Escape') {
            closeMobileNav();
        }

    });


    /* =========================================================
       FLASH MESSAGE AUTO-HIDE
       ========================================================= */

    const flashMessages =
        document.querySelectorAll('.flash');

    if (flashMessages.length) {

        setTimeout(() => {

            flashMessages.forEach(flash => {

                flash.style.opacity = '0';
                flash.style.transform =
                    'translateY(-8px)';

                setTimeout(() => {

                    if (flash.parentNode) {
                        flash.remove();
                    }

                }, 300);

            });

        }, 5000);

    }


    /* =========================================================
       LIGHT / DARK MODE
       ========================================================= */

    const themeToggle =
        document.getElementById('themeToggle');

    const savedTheme =
        localStorage.getItem('theme');

    if (savedTheme === 'dark') {
        document.body.classList.add('dark-mode');
    }

    function updateThemeIcon() {

        if (!themeToggle) return;

        const isDark =
            document.body.classList.contains('dark-mode');

        themeToggle.textContent =
            isDark ? '☀' : '☾';

        themeToggle.setAttribute(
            'aria-label',
            isDark
                ? 'Switch to light mode'
                : 'Switch to dark mode'
        );

        themeToggle.setAttribute(
            'title',
            isDark
                ? 'Switch to light mode'
                : 'Switch to dark mode'
        );

    }

    updateThemeIcon();

    if (themeToggle) {

        themeToggle.addEventListener('click', () => {

            document.body.classList.toggle('dark-mode');

            const isDark =
                document.body.classList.contains('dark-mode');

            localStorage.setItem(
                'theme',
                isDark ? 'dark' : 'light'
            );

            updateThemeIcon();

        });

    }


    /* =========================================================
       NAVBAR SCROLL EFFECT
       ========================================================= */

    const header =
        document.querySelector('header');

    function updateHeader() {

        if (!header) return;

        if (window.scrollY > 30) {

            header.classList.add('scrolled');

        } else {

            header.classList.remove('scrolled');

        }

    }

    updateHeader();

    window.addEventListener(
        'scroll',
        updateHeader,
        { passive: true }
    );


    /* =========================================================
       ACTIVE NAVIGATION LINK
       ========================================================= */

    const currentPath =
        window.location.pathname;

    if (navLinks) {

        navLinks.querySelectorAll('a').forEach(link => {

            const href =
                link.getAttribute('href');

            if (!href || href === '#') return;

            try {

                const linkPath =
                    new URL(
                        href,
                        window.location.origin
                    ).pathname;

                if (
                    linkPath === currentPath &&
                    !link.classList.contains('pill')
                ) {

                    link.classList.add('active');

                }

            } catch (error) {

                return;

            }

        });

    }


    /* =========================================================
       SCROLL PROGRESS
       ========================================================= */

    let progressBar =
        document.getElementById('scrollProgress');

    if (!progressBar) {

        progressBar =
            document.createElement('div');

        progressBar.id =
            'scrollProgress';

        document.body.appendChild(progressBar);

    }

    function updateScrollProgress() {

        const documentHeight =
            document.documentElement.scrollHeight -
            window.innerHeight;

        if (documentHeight <= 0) {

            progressBar.style.width = '0%';
            return;

        }

        const progress =
            (window.scrollY / documentHeight) * 100;

        progressBar.style.width =
            `${Math.min(progress, 100)}%`;

    }

    updateScrollProgress();

    window.addEventListener(
        'scroll',
        updateScrollProgress,
        { passive: true }
    );


    /* =========================================================
       PREMIUM SCROLL REVEAL
       ========================================================= */

    const revealItems =
        document.querySelectorAll(
            '.section, .card, .cats a, .detailgrid, .detailhero, .authbox, .plan-card, .admin-card, .plansummary, .planlist article, .stats > div, .tablewrap'
        );

    revealItems.forEach((item, index) => {

        item.classList.add('reveal');

        item.style.transitionDelay =
            `${Math.min(index * 50, 250)}ms`;

    });


    if ('IntersectionObserver' in window) {

        const revealObserver =
            new IntersectionObserver(
                (entries, observer) => {

                    entries.forEach(entry => {

                        if (entry.isIntersecting) {

                            entry.target.classList.add('show');

                            observer.unobserve(
                                entry.target
                            );

                        }

                    });

                },
                {
                    threshold: 0.1,
                    rootMargin:
                        '0px 0px -30px 0px'
                }
            );

        revealItems.forEach(item => {

            revealObserver.observe(item);

        });

    } else {

        revealItems.forEach(item => {

            item.classList.add('show');

        });

    }


    /* =========================================================
       HERO ENTRANCE ANIMATION
       ========================================================= */

    const hero =
        document.querySelector('.hero');

    if (hero) {

        const heroElements =
            hero.querySelectorAll(
                '.eyebrow, h1, > .container > p:not(.eyebrow), .actions, .heroStat'
            );

        heroElements.forEach((item, index) => {

            item.classList.add('hero-reveal');

            item.style.transitionDelay =
                `${120 + index * 120}ms`;

        });

        requestAnimationFrame(() => {

            hero.classList.add('hero-loaded');

        });

    }


    /* =========================================================
       CARD HOVER
       ========================================================= */

    document.querySelectorAll('.card').forEach(card => {

        card.addEventListener('mouseenter', () => {

            card.classList.add('is-hovered');

        });

        card.addEventListener('mouseleave', () => {

            card.classList.remove('is-hovered');

        });

    });


    /* =========================================================
       PLAN ITEM HOVER
       ========================================================= */

    document.querySelectorAll(
        '.planlist article'
    ).forEach(item => {

        item.addEventListener('mouseenter', () => {

            item.classList.add('plan-hover');

        });

        item.addEventListener('mouseleave', () => {

            item.classList.remove('plan-hover');

        });

    });


    /* =========================================================
       ADMIN TABLE HOVER
       ========================================================= */

    document.querySelectorAll(
        '.tablewrap tr'
    ).forEach(row => {

        row.addEventListener('mouseenter', () => {

            row.classList.add('row-hover');

        });

        row.addEventListener('mouseleave', () => {

            row.classList.remove('row-hover');

        });

    });


    /* =========================================================
       SMOOTH ANCHOR SCROLL
       ========================================================= */

    document.querySelectorAll(
        'a[href^="#"]'
    ).forEach(link => {

        link.addEventListener('click', event => {

            const targetId =
                link.getAttribute('href');

            if (
                !targetId ||
                targetId === '#'
            ) {
                return;
            }

            const target =
                document.querySelector(targetId);

            if (!target) return;

            event.preventDefault();

            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });

        });

    });


    /* =========================================================
       REMOVE FROM PLAN CONFIRMATION
       ========================================================= */

    document.querySelectorAll(
        '.planlist form'
    ).forEach(form => {

        form.addEventListener(
            'submit',
            event => {

                const confirmed =
                    window.confirm(
                        'Remove this place from your plan?'
                    );

                if (!confirmed) {
                    event.preventDefault();
                }

            }
        );

    });


    /* =========================================================
       BUTTON PRESS EFFECT
       ========================================================= */

    document.querySelectorAll(
        '.btn, button'
    ).forEach(button => {

        button.addEventListener(
            'pointerdown',
            () => {
                button.classList.add(
                    'button-pressed'
                );
            }
        );

        button.addEventListener(
            'pointerup',
            () => {
                button.classList.remove(
                    'button-pressed'
                );
            }
        );

        button.addEventListener(
            'pointerleave',
            () => {
                button.classList.remove(
                    'button-pressed'
                );
            }
        );

    });


    /* =========================================================
       REDUCED MOTION SUPPORT
       ========================================================= */

    const prefersReducedMotion =
        window.matchMedia(
            '(prefers-reduced-motion: reduce)'
        ).matches;

    if (prefersReducedMotion) {

        document
            .querySelectorAll(
                '.reveal, .hero-reveal'
            )
            .forEach(item => {

                item.classList.add('show');

                item.style.transitionDelay =
                    '0ms';

            });

    }

});