/* Mahashank — Main JS */

document.addEventListener('DOMContentLoaded', function() {

    // ===== Swiper: Product carousels =====
    document.querySelectorAll('.product-swiper').forEach(function(el) {
        new Swiper(el, {
            slidesPerView: 'auto',
            spaceBetween: 16,
            pagination: {
                el: el.querySelector('.swiper-pagination'),
                clickable: true,
            },
            breakpoints: {
                320: { slidesPerView: 2 },
                640: { slidesPerView: 3 },
                1024: { slidesPerView: 4 },
            }
        });
    });

    // ===== Swiper: Color palette =====
    document.querySelectorAll('.color-swiper').forEach(function(el) {
        new Swiper(el, {
            slidesPerView: 'auto',
            spaceBetween: 20,
            pagination: {
                el: el.querySelector('.swiper-pagination'),
                clickable: true,
            },
            breakpoints: {
                320: { slidesPerView: 2 },
                640: { slidesPerView: 3 },
                1024: { slidesPerView: 5 },
            }
        });
    });

    // ===== Swiper: Info carousel =====
    document.querySelectorAll('.info-swiper').forEach(function(el) {
        new Swiper(el, {
            slidesPerView: 'auto',
            spaceBetween: 20,
            pagination: {
                el: el.querySelector('.swiper-pagination'),
                clickable: true,
            },
            breakpoints: {
                320: { slidesPerView: 1 },
                640: { slidesPerView: 2 },
                1024: { slidesPerView: 3 },
            }
        });
    });

    // ===== Swiper: Instagram carousel =====
    document.querySelectorAll('.instagram-swiper').forEach(function(el) {
        new Swiper(el, {
            slidesPerView: 'auto',
            spaceBetween: 16,
            breakpoints: {
                320: { slidesPerView: 2 },
                640: { slidesPerView: 3 },
                1024: { slidesPerView: 5 },
            }
        });
    });

    // ===== Swiper: Testimonials =====
    document.querySelectorAll('.testimonial-swiper').forEach(function(el) {
        new Swiper(el, {
            slidesPerView: 1,
            spaceBetween: 30,
            loop: true,
            autoplay: {
                delay: 6000,
                disableOnInteraction: false,
            },
            pagination: {
                el: el.querySelector('.swiper-pagination'),
                clickable: true,
            },
            breakpoints: {
                640: { slidesPerView: 2 },
            }
        });
    });
});

// ===== Alpine.js: Countdown component =====
function countdown(deadline) {
    return {
        days: '00',
        hours: '00',
        minutes: '00',
        seconds: '00',

        start() {
            this.tick();
            setInterval(() => this.tick(), 1000);
        },

        tick() {
            const now = new Date().getTime();
            const end = new Date(deadline).getTime();
            const diff = end - now;

            if (diff <= 0) {
                this.days = this.hours = this.minutes = this.seconds = '00';
                return;
            }

            this.days = String(Math.floor(diff / (1000 * 60 * 60 * 24))).padStart(2, '0');
            this.hours = String(Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))).padStart(2, '0');
            this.minutes = String(Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))).padStart(2, '0');
            this.seconds = String(Math.floor((diff % (1000 * 60)) / 1000)).padStart(2, '0');
        }
    };
}

// ===== AJAX add to cart =====
function addToCart(productId, button) {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
    if (!csrfToken) return;

    fetch(`/cart/add/${productId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken.value,
            'X-Requested-With': 'XMLHttpRequest',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update cart badge
            const badge = document.querySelector('.cart-badge');
            if (badge) badge.textContent = data.cart_count;

            // Show toast
            showToast(data.message);
        }
    })
    .catch(err => console.error('Cart error:', err));
}

// ===== Toast notification =====
function showToast(message) {
    const toast = document.createElement('div');
    toast.className = 'fixed top-24 right-4 bg-rw-brown text-white px-6 py-3 rounded-full shadow-lg z-[100] text-sm';
    toast.style.transition = 'all 0.3s';
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(-10px)';
    toast.textContent = message;
    document.body.appendChild(toast);

    requestAnimationFrame(() => {
        toast.style.opacity = '1';
        toast.style.transform = 'translateY(0)';
    });

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(-10px)';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ===== Chatbot (Mistral AI-Powered) =====
function chatbot() {
    return {
        isOpen: false,
        isTyping: false,
        unreadCount: 1,
        inputText: '',
        messages: [],
        csrfToken: '',

        init() {
            // Grab the CSRF token for fetch() calls
            const tokenEl = document.querySelector('[name=csrfmiddlewaretoken]');
            this.csrfToken = tokenEl ? tokenEl.value :
                (window.csrfToken || document.cookie.match(/csrftoken=([^;]+)/)?.[1] || '');

            // Send welcome message after a short delay
            setTimeout(() => {
                if (this.messages.length === 0) {
                    this.messages.push({
                        from: 'bot',
                        text: 'Namaste! 🙏 Welcome to Mahashank! I\'m your AI decor assistant. Ask me about wallpapers, murals, pricing, or how to write great prompts for our AI Generator!'
                    });
                }
            }, 1500);
        },

        async sendMessage() {
            const text = this.inputText.trim();
            if (!text || this.isTyping) return;

            this.messages.push({ from: 'user', text: text });
            this.inputText = '';
            this.scrollToBottom();
            this.isTyping = true;

            try {
                const resp = await fetch('/ai-chat/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.csrfToken,
                    },
                    body: JSON.stringify({
                        message: text,
                        history: this.messages.slice(-7), // last ~7 turns for context
                    }),
                });

                const data = await resp.json();

                if (data.reply) {
                    this.messages.push({ from: 'bot', text: data.reply });
                } else if (data.error) {
                    this.messages.push({ from: 'bot', text: 'Sorry, I had trouble understanding that. Could you try rephrasing?' });
                }
            } catch (err) {
                this.messages.push({
                    from: 'bot',
                    text: 'I\'m having trouble connecting right now. Please try again, or email us at hello@mahashank.com.'
                });
            } finally {
                this.isTyping = false;
                this.scrollToBottom();
            }
        },

        async sendQuickReply(topic) {
            if (this.isTyping) return;

            const questions = {
                'products': 'Tell me about your wallpapers and murals',
                'pricing': 'What are your prices?',
                'shipping': 'How long does shipping take?',
                'installation': 'Do you offer installation?',
                'prompts': 'How do I write a good prompt for the AI Wallpaper Generator?',
            };
            const text = questions[topic] || topic;

            this.messages.push({ from: 'user', text: text });
            this.scrollToBottom();
            this.isTyping = true;

            try {
                const resp = await fetch('/ai-chat/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.csrfToken,
                    },
                    body: JSON.stringify({
                        message: text,
                        history: this.messages.slice(-7),
                    }),
                });

                const data = await resp.json();
                this.messages.push({ from: 'bot', text: data.reply || 'Sorry, I couldn\'t answer that. Please try again.' });
            } catch (err) {
                this.messages.push({
                    from: 'bot',
                    text: 'I\'m having trouble connecting right now. Please try again, or email us at hello@mahashank.com.'
                });
            } finally {
                this.isTyping = false;
                this.scrollToBottom();
            }
        },

        scrollToBottom() {
            this.$nextTick(() => {
                if (this.$refs.messages) {
                    this.$refs.messages.scrollTop = this.$refs.messages.scrollHeight;
                }
            });
        }
    };
}
