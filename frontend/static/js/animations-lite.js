/* ============================================================
   MEDZOON LITE ANIMATIONS (Performance Optimized)
   Version: 2.0 - Lightweight
   Size: ~2KB (vs 10KB original)
   Features: Essential animations only, no heavy observers
   ============================================================ */

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', function() {
    initCounters();
    initSmoothScroll();
});

// ============== COUNTER ANIMATIONS (Simplified) ==============
function initCounters() {
    const counters = document.querySelectorAll('.stat-number[data-count]');

    // Simple scroll trigger without IntersectionObserver
    let hasAnimated = false;

    function checkScroll() {
        if (hasAnimated) return;

        const scrollY = window.scrollY || window.pageYOffset;
        const windowHeight = window.innerHeight;

        counters.forEach(counter => {
            const rect = counter.getBoundingClientRect();
            const isVisible = rect.top < windowHeight && rect.bottom > 0;

            if (isVisible && !counter.hasAttribute('data-animated')) {
                animateCounter(counter);
                counter.setAttribute('data-animated', 'true');
            }
        });

        // Check if all animated
        const allAnimated = Array.from(counters).every(c => c.hasAttribute('data-animated'));
        if (allAnimated) {
            hasAnimated = true;
            window.removeEventListener('scroll', checkScroll);
        }
    }

    // Initial check
    setTimeout(checkScroll, 100);

    // Scroll listener (with passive for performance)
    window.addEventListener('scroll', checkScroll, { passive: true });
}

function animateCounter(element) {
    const target = parseInt(element.getAttribute('data-count') || element.textContent);
    const duration = 1500; // 1.5 seconds
    const startTime = performance.now();

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);

        // Easing function (ease-out)
        const easeOut = 1 - Math.pow(1 - progress, 3);
        const current = Math.floor(easeOut * target);

        element.textContent = current.toLocaleString();

        if (progress < 1) {
            requestAnimationFrame(update);
        } else {
            element.textContent = target.toLocaleString();
        }
    }

    requestAnimationFrame(update);
}

// ============== SMOOTH SCROLL ==============
function initSmoothScroll() {
    // Only for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href === '#' || href === '#!') return;

            const target = document.querySelector(href);
            if (!target) return;

            e.preventDefault();

            const headerOffset = 80;
            const elementPosition = target.getBoundingClientRect().top;
            const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

            window.scrollTo({
                top: offsetPosition,
                behavior: 'smooth'
            });
        });
    });
}

// ============== TOAST NOTIFICATIONS (Minimal) ==============
window.showToast = function(message, type = 'info', duration = 3000) {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        background: ${type === 'success' ? '#10B981' : type === 'error' ? '#EF4444' : '#1E88E5'};
        color: white;
        border-radius: 0.5rem;
        box-shadow: 0 10px 15px rgba(0,0,0,0.1);
        z-index: 9999;
        animation: slideIn 0.3s ease-out;
    `;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => toast.remove(), 300);
    }, duration);
};

// Add animation keyframes dynamically
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
