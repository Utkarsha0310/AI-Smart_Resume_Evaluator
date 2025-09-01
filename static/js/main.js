// ===== AI Resume Evaluator - Main JavaScript =====

// Global theme management
class ThemeManager {
    constructor() {
        this.currentTheme = this.getStoredTheme() || 'dark';
        this.init();
    }

    init() {
        this.applyTheme(this.currentTheme);
        this.setupThemeToggle();
        this.fetchCurrentTheme();
    }

    getStoredTheme() {
        return localStorage.getItem('resume-evaluator-theme');
    }

    storeTheme(theme) {
        localStorage.setItem('resume-evaluator-theme', theme);
    }

    applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        this.updateThemeIcon(theme);
        this.storeTheme(theme);
    }

    updateThemeIcon(theme) {
        const themeIcon = document.getElementById('themeIcon');
        if (themeIcon) {
            themeIcon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
        }
    }

    setupThemeToggle() {
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => {
                this.toggleTheme();
            });
        }
    }

    toggleTheme() {
        const newTheme = this.currentTheme === 'dark' ? 'light' : 'dark';
        this.currentTheme = newTheme;
        this.applyTheme(newTheme);
        
        // Sync with server
        this.syncThemeWithServer(newTheme);
    }

    async fetchCurrentTheme() {
        try {
            const response = await fetch('/api/get-theme');
            const data = await response.json();
            if (data.theme && data.theme !== this.currentTheme) {
                this.currentTheme = data.theme;
                this.applyTheme(data.theme);
            }
        } catch (error) {
            console.warn('Failed to fetch theme from server:', error);
        }
    }

    async syncThemeWithServer(theme) {
        try {
            await fetch('/api/toggle-theme', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ theme })
            });
        } catch (error) {
            console.warn('Failed to sync theme with server:', error);
        }
    }
}

// Utility functions
const Utils = {
    // Debounce function
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // Throttle function
    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },

    // Format file size
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },

    // Format percentage
    formatPercentage(value, decimals = 1) {
        return `${parseFloat(value).toFixed(decimals)}%`;
    },

    // Animate number counting
    animateNumber(element, start, end, duration = 1000) {
        const startTime = performance.now();
        const difference = end - start;

        function updateNumber(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Easing function
            const easeOut = 1 - Math.pow(1 - progress, 3);
            const current = start + (difference * easeOut);
            
            element.textContent = Math.round(current);
            
            if (progress < 1) {
                requestAnimationFrame(updateNumber);
            }
        }
        
        requestAnimationFrame(updateNumber);
    },

    // Show loading state
    showLoading(element) {
        element.classList.add('loading');
        element.style.pointerEvents = 'none';
    },

    // Hide loading state
    hideLoading(element) {
        element.classList.remove('loading');
        element.style.pointerEvents = 'auto';
    },

    // Show toast notification
    showToast(message, type = 'info', duration = 3000) {
        const toast = document.createElement('div');
        toast.className = `toast-notification toast-${type}`;
        toast.innerHTML = `
            <div class="toast-content">
                <i class="fas fa-${this.getToastIcon(type)} me-2"></i>
                <span>${message}</span>
            </div>
            <button class="toast-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;

        // Add toast styles if not already present
        if (!document.getElementById('toast-styles')) {
            const styles = document.createElement('style');
            styles.id = 'toast-styles';
            styles.textContent = `
                .toast-notification {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    z-index: 9999;
                    min-width: 300px;
                    padding: 1rem;
                    border-radius: 0.5rem;
                    color: white;
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    animation: slideInRight 0.3s ease;
                }
                .toast-success { background: var(--success); }
                .toast-error { background: var(--danger); }
                .toast-warning { background: var(--warning); }
                .toast-info { background: var(--info); }
                .toast-close {
                    background: none;
                    border: none;
                    color: white;
                    cursor: pointer;
                    padding: 0.25rem;
                }
                @keyframes slideInRight {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
            `;
            document.head.appendChild(styles);
        }

        document.body.appendChild(toast);

        // Auto remove after duration
        setTimeout(() => {
            if (toast.parentElement) {
                toast.style.animation = 'slideInRight 0.3s ease reverse';
                setTimeout(() => toast.remove(), 300);
            }
        }, duration);
    },

    getToastIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }
};

// Form validation helper
class FormValidator {
    constructor(form) {
        this.form = form;
        this.errors = new Map();
    }

    validateFile(input, allowedTypes = ['pdf'], maxSize = 16 * 1024 * 1024) {
        const file = input.files[0];
        if (!file) {
            this.addError(input.name, 'Please select a file');
            return false;
        }

        // Check file type
        const fileType = file.type.split('/')[1];
        if (!allowedTypes.includes(fileType)) {
            this.addError(input.name, `Only ${allowedTypes.join(', ')} files are allowed`);
            return false;
        }

        // Check file size
        if (file.size > maxSize) {
            this.addError(input.name, `File size must be less than ${Utils.formatFileSize(maxSize)}`);
            return false;
        }

        this.removeError(input.name);
        return true;
    }

    addError(fieldName, message) {
        this.errors.set(fieldName, message);
        this.displayError(fieldName, message);
    }

    removeError(fieldName) {
        this.errors.delete(fieldName);
        this.clearError(fieldName);
    }

    displayError(fieldName, message) {
        const field = this.form.querySelector(`[name="${fieldName}"]`);
        if (field) {
            field.classList.add('is-invalid');
            
            // Remove existing error message
            const existingError = field.parentElement.querySelector('.invalid-feedback');
            if (existingError) {
                existingError.remove();
            }

            // Add new error message
            const errorDiv = document.createElement('div');
            errorDiv.className = 'invalid-feedback';
            errorDiv.textContent = message;
            field.parentElement.appendChild(errorDiv);
        }
    }

    clearError(fieldName) {
        const field = this.form.querySelector(`[name="${fieldName}"]`);
        if (field) {
            field.classList.remove('is-invalid');
            const errorDiv = field.parentElement.querySelector('.invalid-feedback');
            if (errorDiv) {
                errorDiv.remove();
            }
        }
    }

    isValid() {
        return this.errors.size === 0;
    }

    getErrors() {
        return Array.from(this.errors.entries());
    }
}

// Analytics and tracking
class Analytics {
    constructor() {
        this.sessionStart = Date.now();
        this.events = [];
    }

    track(eventName, properties = {}) {
        const event = {
            name: eventName,
            properties: {
                ...properties,
                timestamp: Date.now(),
                sessionDuration: Date.now() - this.sessionStart,
                url: window.location.href,
                userAgent: navigator.userAgent
            }
        };
        
        this.events.push(event);
        console.log('Analytics Event:', event);
        
        // Here you could send to an analytics service
        // this.sendToAnalytics(event);
    }

    getSessionStats() {
        return {
            duration: Date.now() - this.sessionStart,
            eventCount: this.events.length,
            events: this.events
        };
    }
}

// Progress tracking
class ProgressTracker {
    constructor() {
        this.steps = [];
        this.currentStep = 0;
    }

    addStep(name, description) {
        this.steps.push({ name, description, completed: false });
    }

    completeStep(index) {
        if (index < this.steps.length) {
            this.steps[index].completed = true;
            this.currentStep = Math.max(this.currentStep, index + 1);
            this.updateProgressBar();
        }
    }

    updateProgressBar() {
        const progressBars = document.querySelectorAll('.progress-tracker');
        progressBars.forEach(bar => {
            const percentage = (this.currentStep / this.steps.length) * 100;
            const progressFill = bar.querySelector('.progress-fill');
            if (progressFill) {
                progressFill.style.width = `${percentage}%`;
            }
        });
    }

    getProgress() {
        return {
            current: this.currentStep,
            total: this.steps.length,
            percentage: (this.currentStep / this.steps.length) * 100,
            steps: this.steps
        };
    }
}

// Performance monitor
class PerformanceMonitor {
    constructor() {
        this.metrics = new Map();
        this.startTime = performance.now();
    }

    mark(name) {
        this.metrics.set(name, performance.now());
    }

    measure(name, startMark) {
        const endTime = performance.now();
        const startTime = this.metrics.get(startMark) || this.startTime;
        const duration = endTime - startTime;
        
        console.log(`Performance: ${name} took ${duration.toFixed(2)}ms`);
        return duration;
    }

    getMetrics() {
        return Object.fromEntries(this.metrics);
    }
}

// Global instances
let themeManager;
let analytics;
let performanceMonitor;

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize global components
    themeManager = new ThemeManager();
    analytics = new Analytics();
    performanceMonitor = new PerformanceMonitor();

    // Track page load
    analytics.track('page_load', {
        page: window.location.pathname,
        loadTime: performance.now()
    });

    // Add smooth scrolling
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add loading states to forms
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                Utils.showLoading(submitBtn);
                submitBtn.disabled = true;
            }
        });
    });

    // Add hover effects to cards
    document.querySelectorAll('.card-navy').forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    // Add click ripple effect to buttons
    document.querySelectorAll('.btn').forEach(button => {
        button.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.cssText = `
                position: absolute;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.3);
                transform: scale(0);
                animation: ripple 0.6s linear;
                left: ${x}px;
                top: ${y}px;
                width: ${size}px;
                height: ${size}px;
                pointer-events: none;
            `;
            
            this.style.position = 'relative';
            this.style.overflow = 'hidden';
            this.appendChild(ripple);
            
            setTimeout(() => ripple.remove(), 600);
        });
    });

    // Add CSS for ripple animation if not present
    if (!document.getElementById('ripple-styles')) {
        const styles = document.createElement('style');
        styles.id = 'ripple-styles';
        styles.textContent = `
            @keyframes ripple {
                to {
                    transform: scale(4);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(styles);
    }

    // Lazy load images
    const images = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                imageObserver.unobserve(img);
            }
        });
    });

    images.forEach(img => {
        imageObserver.observe(img);
    });

    // Add keyboard navigation
    document.addEventListener('keydown', function(e) {
        // Escape key closes modals
        if (e.key === 'Escape') {
            const modals = document.querySelectorAll('.modal.show');
            modals.forEach(modal => {
                const modalInstance = bootstrap.Modal.getInstance(modal);
                if (modalInstance) {
                    modalInstance.hide();
                }
            });
        }
        
        // Ctrl/Cmd + K for search (if implemented)
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.querySelector('input[type="search"]');
            if (searchInput) {
                searchInput.focus();
            }
        }
    });

    // Monitor connection status
    function updateConnectionStatus() {
        const isOnline = navigator.onLine;
        if (!isOnline) {
            Utils.showToast('You are offline. Some features may not work.', 'warning', 5000);
        }
    }

    window.addEventListener('online', () => {
        Utils.showToast('Connection restored!', 'success');
    });

    window.addEventListener('offline', updateConnectionStatus);

    // Performance monitoring
    window.addEventListener('load', function() {
        performanceMonitor.mark('page_loaded');
        
        // Log performance metrics
        setTimeout(() => {
            const navigation = performance.getEntriesByType('navigation')[0];
            if (navigation) {
                analytics.track('performance', {
                    domContentLoaded: navigation.domContentLoadedEventEnd,
                    loadComplete: navigation.loadEventEnd,
                    firstPaint: performance.getEntriesByType('paint')[0]?.startTime,
                    timeToInteractive: performance.now()
                });
            }
        }, 1000);
    });

    // Track user interactions
    ['click', 'scroll', 'resize'].forEach(eventType => {
        window.addEventListener(eventType, Utils.throttle(() => {
            analytics.track(`user_${eventType}`, {
                timestamp: Date.now(),
                viewport: {
                    width: window.innerWidth,
                    height: window.innerHeight
                }
            });
        }, 1000));
    });

    console.log('AI Resume Evaluator initialized successfully');
});

// Export utilities for use in other scripts
window.ResumeEvaluator = {
    Utils,
    FormValidator,
    Analytics,
    ProgressTracker,
    PerformanceMonitor,
    themeManager: () => themeManager,
    analytics: () => analytics,
    performanceMonitor: () => performanceMonitor
};
