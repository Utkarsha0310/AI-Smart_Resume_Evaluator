// ===== Confetti Animation System =====

class ConfettiManager {
    constructor() {
        this.isAnimating = false;
        this.particles = [];
        this.canvas = null;
        this.ctx = null;
        this.animationId = null;
    }

    // Basic confetti burst using canvas-confetti library
    triggerBasicConfetti() {
        if (typeof confetti === 'undefined') {
            console.warn('Confetti library not loaded');
            return;
        }

        confetti({
            particleCount: 100,
            spread: 70,
            origin: { y: 0.6 },
            colors: ['#0A192F', '#1F4068', '#162447', '#3A7BD5', '#22C55E', '#F59E0B']
        });
    }

    // Advanced confetti with custom animations
    triggerAdvancedConfetti() {
        if (typeof confetti === 'undefined') {
            this.createCustomConfetti();
            return;
        }

        const duration = 3000;
        const animationEnd = Date.now() + duration;
        const defaults = { 
            startVelocity: 30, 
            spread: 360, 
            ticks: 60, 
            zIndex: 9999,
            colors: ['#0A192F', '#1F4068', '#162447', '#3A7BD5', '#22C55E', '#F59E0B', '#EF4444']
        };

        function randomInRange(min, max) {
            return Math.random() * (max - min) + min;
        }

        const interval = setInterval(() => {
            const timeLeft = animationEnd - Date.now();

            if (timeLeft <= 0) {
                clearInterval(interval);
                return;
            }

            const particleCount = 50 * (timeLeft / duration);

            // Left side burst
            confetti({
                ...defaults,
                particleCount,
                origin: { x: randomInRange(0.1, 0.3), y: Math.random() - 0.2 }
            });

            // Right side burst
            confetti({
                ...defaults,
                particleCount,
                origin: { x: randomInRange(0.7, 0.9), y: Math.random() - 0.2 }
            });
        }, 250);
    }

    // Celebration for high scores
    triggerCelebrationConfetti() {
        if (typeof confetti === 'undefined') {
            this.createCustomConfetti();
            return;
        }

        // Fire multiple bursts
        const count = 200;
        const defaults = {
            origin: { y: 0.7 },
            zIndex: 9999
        };

        function fire(particleRatio, opts) {
            confetti({
                ...defaults,
                ...opts,
                particleCount: Math.floor(count * particleRatio),
                colors: ['#FFD700', '#FFA500', '#FF6347', '#98FB98', '#87CEEB', '#DDA0DD']
            });
        }

        fire(0.25, {
            spread: 26,
            startVelocity: 55,
        });

        fire(0.2, {
            spread: 60,
        });

        fire(0.35, {
            spread: 100,
            decay: 0.91,
            scalar: 0.8
        });

        fire(0.1, {
            spread: 120,
            startVelocity: 25,
            decay: 0.92,
            scalar: 1.2
        });

        fire(0.1, {
            spread: 120,
            startVelocity: 45,
        });
    }

    // Custom confetti implementation (fallback)
    createCustomConfetti() {
        if (this.isAnimating) return;

        this.setupCanvas();
        this.createParticles();
        this.animate();
    }

    setupCanvas() {
        this.canvas = document.createElement('canvas');
        this.canvas.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            pointer-events: none;
            z-index: 9999;
        `;
        
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
        this.ctx = this.canvas.getContext('2d');
        
        document.body.appendChild(this.canvas);
    }

    createParticles() {
        const colors = ['#0A192F', '#1F4068', '#162447', '#3A7BD5', '#22C55E', '#F59E0B', '#EF4444'];
        const shapes = ['circle', 'square', 'triangle'];
        
        this.particles = [];
        
        for (let i = 0; i < 100; i++) {
            this.particles.push({
                x: Math.random() * this.canvas.width,
                y: this.canvas.height + 10,
                vx: (Math.random() - 0.5) * 6,
                vy: -(Math.random() * 15 + 10),
                gravity: 0.3,
                life: 1,
                decay: Math.random() * 0.015 + 0.01,
                color: colors[Math.floor(Math.random() * colors.length)],
                shape: shapes[Math.floor(Math.random() * shapes.length)],
                size: Math.random() * 8 + 4,
                rotation: Math.random() * 360,
                rotationSpeed: (Math.random() - 0.5) * 10
            });
        }
    }

    animate() {
        if (!this.ctx || !this.canvas) return;

        this.isAnimating = true;
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        for (let i = this.particles.length - 1; i >= 0; i--) {
            const particle = this.particles[i];
            
            // Update physics
            particle.vy += particle.gravity;
            particle.x += particle.vx;
            particle.y += particle.vy;
            particle.life -= particle.decay;
            particle.rotation += particle.rotationSpeed;

            // Remove dead particles
            if (particle.life <= 0 || particle.y > this.canvas.height + 50) {
                this.particles.splice(i, 1);
                continue;
            }

            // Draw particle
            this.ctx.save();
            this.ctx.globalAlpha = particle.life;
            this.ctx.translate(particle.x, particle.y);
            this.ctx.rotate(particle.rotation * Math.PI / 180);
            this.ctx.fillStyle = particle.color;

            switch (particle.shape) {
                case 'circle':
                    this.ctx.beginPath();
                    this.ctx.arc(0, 0, particle.size / 2, 0, Math.PI * 2);
                    this.ctx.fill();
                    break;
                case 'square':
                    this.ctx.fillRect(-particle.size / 2, -particle.size / 2, particle.size, particle.size);
                    break;
                case 'triangle':
                    this.ctx.beginPath();
                    this.ctx.moveTo(0, -particle.size / 2);
                    this.ctx.lineTo(-particle.size / 2, particle.size / 2);
                    this.ctx.lineTo(particle.size / 2, particle.size / 2);
                    this.ctx.closePath();
                    this.ctx.fill();
                    break;
            }
            
            this.ctx.restore();
        }

        if (this.particles.length > 0) {
            this.animationId = requestAnimationFrame(() => this.animate());
        } else {
            this.cleanup();
        }
    }

    cleanup() {
        this.isAnimating = false;
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
            this.animationId = null;
        }
        if (this.canvas && this.canvas.parentNode) {
            this.canvas.parentNode.removeChild(this.canvas);
        }
        this.canvas = null;
        this.ctx = null;
        this.particles = [];
    }

    // Score-based confetti trigger
    triggerForScore(score) {
        if (score >= 90) {
            this.triggerCelebrationConfetti();
        } else if (score >= 80) {
            this.triggerAdvancedConfetti();
        } else if (score >= 70) {
            this.triggerBasicConfetti();
        }
    }
}

// Score Animation
class ScoreAnimator {
    constructor() {
        this.animationDuration = 2000;
        this.confettiManager = new ConfettiManager();
    }

    animateScore(element, targetScore, options = {}) {
        const {
            duration = this.animationDuration,
            startScore = 0,
            triggerConfetti = true,
            onComplete = null
        } = options;

        if (!element) return;

        const scoreNumber = element.querySelector('.score-number') || element;
        const startTime = performance.now();

        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);

            // Easing function (ease-out cubic)
            const easeOut = 1 - Math.pow(1 - progress, 3);
            const currentScore = startScore + (targetScore - startScore) * easeOut;

            // Update score display
            scoreNumber.textContent = Math.round(currentScore);

            // Update circle progress if it's a circular score
            if (element.classList.contains('score-circle')) {
                element.style.setProperty('--score', currentScore);
                
                // Color transition based on score
                const hue = (currentScore / 100) * 120; // Red (0) to green (120)
                element.style.setProperty('--score-color', `hsl(${hue}, 70%, 50%)`);
            }

            // Continue animation
            if (progress < 1) {
                requestAnimationFrame(animate);
            } else {
                // Animation complete
                if (triggerConfetti && targetScore >= 80) {
                    setTimeout(() => {
                        this.confettiManager.triggerForScore(targetScore);
                    }, 300);
                }
                
                if (onComplete) {
                    onComplete();
                }
            }
        };

        requestAnimationFrame(animate);
    }

    animateProgressBar(element, targetPercentage, options = {}) {
        const {
            duration = 1000,
            color = null,
            onComplete = null
        } = options;

        if (!element) return;

        const progressBar = element.querySelector('.progress-bar') || element;
        const startTime = performance.now();

        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);

            const easeOut = 1 - Math.pow(1 - progress, 3);
            const currentWidth = targetPercentage * easeOut;

            progressBar.style.width = `${currentWidth}%`;

            if (color) {
                progressBar.style.backgroundColor = color;
            }

            if (progress < 1) {
                requestAnimationFrame(animate);
            } else if (onComplete) {
                onComplete();
            }
        };

        requestAnimationFrame(animate);
    }

    staggeredScoreAnimation(scoreElements, scores, options = {}) {
        const {
            staggerDelay = 200,
            ...animationOptions
        } = options;

        scoreElements.forEach((element, index) => {
            setTimeout(() => {
                this.animateScore(element, scores[index], {
                    ...animationOptions,
                    triggerConfetti: index === scoreElements.length - 1 && scores[index] >= 80
                });
            }, index * staggerDelay);
        });
    }
}

// Celebration Effects
class CelebrationEffects {
    constructor() {
        this.confettiManager = new ConfettiManager();
        this.scoreAnimator = new ScoreAnimator();
    }

    celebrateHighScore(score, element) {
        // Animate the score
        this.scoreAnimator.animateScore(element, score, {
            triggerConfetti: false,
            onComplete: () => {
                // Add achievement badge
                this.showAchievementBadge(score);
                
                // Trigger confetti
                setTimeout(() => {
                    this.confettiManager.triggerForScore(score);
                }, 500);
                
                // Add pulsing effect
                element.classList.add('animate-bounce');
                setTimeout(() => {
                    element.classList.remove('animate-bounce');
                }, 1000);
            }
        });

        // Add background glow effect
        this.addGlowEffect(element);
    }

    showAchievementBadge(score) {
        const badge = document.createElement('div');
        badge.className = 'achievement-notification';
        
        let badgeContent = '';
        if (score >= 95) {
            badgeContent = '<i class="fas fa-trophy"></i> Outstanding Performance!';
        } else if (score >= 90) {
            badgeContent = '<i class="fas fa-star"></i> Excellent Work!';
        } else if (score >= 80) {
            badgeContent = '<i class="fas fa-medal"></i> Great Job!';
        }

        badge.innerHTML = badgeContent;
        badge.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) scale(0);
            background: linear-gradient(135deg, #FFD700, #FFA500);
            color: white;
            padding: 1rem 2rem;
            border-radius: 2rem;
            font-size: 1.2rem;
            font-weight: 600;
            z-index: 10000;
            box-shadow: 0 10px 30px rgba(255, 215, 0, 0.3);
            animation: achievementPop 2s ease-in-out forwards;
        `;

        // Add animation styles
        if (!document.getElementById('achievement-styles')) {
            const styles = document.createElement('style');
            styles.id = 'achievement-styles';
            styles.textContent = `
                @keyframes achievementPop {
                    0% { transform: translate(-50%, -50%) scale(0); opacity: 0; }
                    20% { transform: translate(-50%, -50%) scale(1.2); opacity: 1; }
                    40% { transform: translate(-50%, -50%) scale(1); }
                    80% { transform: translate(-50%, -50%) scale(1); opacity: 1; }
                    100% { transform: translate(-50%, -50%) scale(0); opacity: 0; }
                }
            `;
            document.head.appendChild(styles);
        }

        document.body.appendChild(badge);

        setTimeout(() => {
            if (badge.parentNode) {
                badge.remove();
            }
        }, 2000);
    }

    addGlowEffect(element) {
        element.style.boxShadow = '0 0 30px rgba(58, 123, 213, 0.6)';
        element.style.transition = 'box-shadow 0.5s ease';
        
        setTimeout(() => {
            element.style.boxShadow = '';
        }, 3000);
    }

    pulseElement(element, duration = 1000) {
        element.style.animation = `pulse ${duration}ms ease-in-out`;
        
        setTimeout(() => {
            element.style.animation = '';
        }, duration);
    }
}

// Global confetti functions
function triggerConfetti() {
    const confettiManager = new ConfettiManager();
    confettiManager.triggerBasicConfetti();
}

function triggerCelebrationConfetti() {
    const confettiManager = new ConfettiManager();
    confettiManager.triggerCelebrationConfetti();
}

function celebrateScore(score, element) {
    const celebration = new CelebrationEffects();
    celebration.celebrateHighScore(score, element);
}

// Export for use in other scripts
window.ConfettiSystem = {
    ConfettiManager,
    ScoreAnimator,
    CelebrationEffects,
    triggerConfetti,
    triggerCelebrationConfetti,
    celebrateScore
};
