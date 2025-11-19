/* =================================================================
   MEDZOON ANIMATIONS & INTERACTIONS
   Version: 1.0.0
   Features: Counter Animations, Smooth Scroll, AOS, Navbar Effects
   ================================================================= */

// ============== DOCUMENT READY ==============
document.addEventListener('DOMContentLoaded', function() {
    initCounterAnimations();
    initSmoothScroll();
    initNavbarScroll();
    initAOSAnimations();
    initCardAnimations();
});

// ============== COUNTER ANIMATIONS (Statistics) ==============
function initCounterAnimations() {
    const counters = document.querySelectorAll('.stat-number, [data-counter]');

    const counterObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const counter = entry.target;
                const target = parseInt(counter.getAttribute('data-count') || counter.innerText.replace(/\D/g, ''));
                const duration = 2000; // 2 seconds
                const increment = target / (duration / 16); // 60fps
                let current = 0;

                const updateCounter = () => {
                    current += increment;
                    if (current < target) {
                        counter.innerText = Math.floor(current).toLocaleString();
                        requestAnimationFrame(updateCounter);
                    } else {
                        counter.innerText = target.toLocaleString();
                    }
                };

                updateCounter();
                counterObserver.unobserve(counter);
            }
        });
    }, { threshold: 0.5 });

    counters.forEach(counter => counterObserver.observe(counter));
}

// ============== SMOOTH SCROLL ==============
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href === '#') return;

            e.preventDefault();
            const target = document.querySelector(href);

            if (target) {
                const headerOffset = 80;
                const elementPosition = target.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
}

// ============== NAVBAR SCROLL EFFECTS ==============
function initNavbarScroll() {
    const navbar = document.querySelector('.navbar-medzoon');
    if (!navbar) return;

    let lastScroll = 0;

    window.addEventListener('scroll', () => {
        const currentScroll = window.pageYOffset;

        // Add 'scrolled' class when scrolling down
        if (currentScroll > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }

        lastScroll = currentScroll;
    });
}

// ============== AOS (Animate On Scroll) INITIALIZATION ==============
function initAOSAnimations() {
    // Check if AOS library is loaded
    if (typeof AOS !== 'undefined') {
        AOS.init({
            duration: 800,
            easing: 'ease-out',
            once: true,
            offset: 100,
            delay: 100
        });
    } else {
        // Fallback: Add manual intersection observer for fade-in effects
        const animatedElements = document.querySelectorAll('[data-animate]');

        const fadeObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in-up');
                    fadeObserver.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });

        animatedElements.forEach(el => fadeObserver.observe(el));
    }
}

// ============== CARD HOVER EFFECTS ==============
function initCardAnimations() {
    const cards = document.querySelectorAll('.service-card, .doctor-card, .card-medzoon');

    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px)';
        });

        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
}

// ============== LOADING ANIMATION ==============
function showLoading() {
    const loader = document.createElement('div');
    loader.id = 'page-loader';
    loader.innerHTML = `
        <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                    background: linear-gradient(135deg, #0A2463 0%, #1E88E5 100%);
                    display: flex; align-items: center; justify-content: center;
                    z-index: 9999;">
            <div style="text-align: center; color: white;">
                <div class="spinner-border" role="status" style="width: 3rem; height: 3rem; border-width: 4px;">
                    <span class="visually-hidden">Cargando...</span>
                </div>
                <p style="margin-top: 1rem; font-size: 1.25rem; font-weight: 600;">Cargando...</p>
            </div>
        </div>
    `;
    document.body.appendChild(loader);
}

function hideLoading() {
    const loader = document.getElementById('page-loader');
    if (loader) {
        loader.style.opacity = '0';
        loader.style.transition = 'opacity 0.5s ease';
        setTimeout(() => loader.remove(), 500);
    }
}

// ============== MODAL HELPERS ==============
function showModal(title, message, type = 'info') {
    const modalHTML = `
        <div class="modal fade" id="dynamicModal" tabindex="-1">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content" style="border-radius: 1.25rem; overflow: hidden;">
                    <div class="modal-header" style="background: linear-gradient(135deg, #0A2463 0%, #1E88E5 100%); color: white; border: none;">
                        <h5 class="modal-title" style="font-family: 'Poppins', sans-serif; font-weight: 700;">${title}</h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body" style="padding: 2rem; font-size: 1rem;">
                        ${message}
                    </div>
                    <div class="modal-footer" style="border: none; padding: 1rem 2rem;">
                        <button type="button" class="btn btn-primary-medzoon" data-bs-dismiss="modal">Entendido</button>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Remove existing modal if any
    const existingModal = document.getElementById('dynamicModal');
    if (existingModal) existingModal.remove();

    // Add new modal
    document.body.insertAdjacentHTML('beforeend', modalHTML);

    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('dynamicModal'));
    modal.show();

    // Remove from DOM after hidden
    document.getElementById('dynamicModal').addEventListener('hidden.bs.modal', function() {
        this.remove();
    });
}

// ============== TOAST NOTIFICATIONS ==============
function showToast(message, type = 'success') {
    const toastColors = {
        success: 'linear-gradient(135deg, #10B981, #059669)',
        error: 'linear-gradient(135deg, #EF4444, #DC2626)',
        warning: 'linear-gradient(135deg, #F59E0B, #D97706)',
        info: 'linear-gradient(135deg, #1E88E5, #0A2463)'
    };

    const toast = document.createElement('div');
    toast.className = 'toast-notification';
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${toastColors[type] || toastColors.info};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 1rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        z-index: 10000;
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        animation: slideInRight 0.3s ease-out;
        max-width: 400px;
    `;
    toast.textContent = message;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideOutRight 0.3s ease-out';
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ============== FORM VALIDATION HELPERS ==============
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;

    let isValid = true;
    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');

    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
            input.classList.add('is-valid');
        }
    });

    return isValid;
}

// ============== SCROLL ANIMATIONS ==============
function animateOnScroll() {
    const elements = document.querySelectorAll('[data-scroll-animate]');

    const scrollObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const animationType = entry.target.getAttribute('data-scroll-animate');
                entry.target.classList.add(animationType);
                scrollObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.2 });

    elements.forEach(el => scrollObserver.observe(el));
}

// Initialize scroll animations
animateOnScroll();

// ============== EXPORT FUNCTIONS ==============
window.MedzoonAnimations = {
    showLoading,
    hideLoading,
    showModal,
    showToast,
    validateForm,
    initCounterAnimations,
    initSmoothScroll,
    initNavbarScroll
};

// ============== CSS FOR TOAST ANIMATIONS ==============
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(100px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }

    @keyframes slideOutRight {
        from {
            opacity: 1;
            transform: translateX(0);
        }
        to {
            opacity: 0;
            transform: translateX(100px);
        }
    }
`;
document.head.appendChild(style);