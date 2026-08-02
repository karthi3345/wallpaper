/* Mahashanka — Main JS */

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

// ===== Chatbot =====
function chatbot() {
    return {
        isOpen: false,
        isTyping: false,
        unreadCount: 1,
        inputText: '',
        messages: [],

        init() {
            // Send welcome message after a short delay
            setTimeout(() => {
                if (this.messages.length === 0) {
                    this.messages.push({
                        from: 'bot',
                        text: 'Namaste! 🙏 Welcome to Mahashanka. How can we help you transform your walls today?'
                    });
                }
            }, 1500);
        },

        sendMessage() {
            const text = this.inputText.trim();
            if (!text) return;

            this.messages.push({ from: 'user', text: text });
            this.inputText = '';
            this.scrollToBottom();

            // Simulate bot response
            this.isTyping = true;
            setTimeout(() => {
                this.isTyping = false;
                this.messages.push({ from: 'bot', text: this.getReply(text) });
                this.scrollToBottom();
            }, 800 + Math.random() * 700);
        },

        sendQuickReply(topic) {
            const questions = {
                'products': 'Tell me about your wallpapers and murals',
                'pricing': 'What are your prices?',
                'shipping': 'How long does shipping take?',
                'installation': 'Do you offer installation?',
            };
            this.messages.push({ from: 'user', text: questions[topic] });
            this.scrollToBottom();
            this.isTyping = true;
            setTimeout(() => {
                this.isTyping = false;
                this.messages.push({ from: 'bot', text: this.getReply(questions[topic]) });
                this.scrollToBottom();
            }, 800 + Math.random() * 400);
        },

        getReply(input) {
            const text = input.toLowerCase();

            // Greetings
            if (/hello|hi|hey|namaste|good (morning|evening|afternoon)/.test(text)) {
                return 'Hello! How can I assist you today? You can ask me about our wallpapers, murals, pricing, or shipping. 😊';
            }

            // Products
            if (/wallpaper|roll|design|pattern/.test(text)) {
                return 'We have a wide range of wallpapers including Luxury Series, Damask, Floral, Abstract, Metallic, and more. Prices start from ₹85/sqft. Browse our collection at the Shop page!';
            }
            if (/mural|heritage|pichwai|peacock|temple|tropical/.test(text)) {
                return 'Our Wall Murals are stunning! We offer Heritage, European, Pichwai, Temple, Tropical, 3D, and Peacock designs. Each is custom-made to your wall dimensions. Would you like to see our best sellers?';
            }
            if (/kids|nursery|children/.test(text)) {
                return 'We have delightful Kids & Nursery wallpapers featuring playful patterns and themes. Perfect for creating a magical space for little ones! 🧸';
            }
            if (/mosaic|tile|glass/.test(text)) {
                return 'Our Glass Mosaic Tiles are perfect for adding elegance to kitchens, bathrooms, and feature walls. Available in multiple colors and finishes.';
            }
            if (/painting|wall.?art|canvas/.test(text)) {
                return 'Our Paintings & Wallart collection features curated pieces from talented artists. Each piece adds a unique character to your space.';
            }
            if (/self.?adhesive|peel.?stick|stick.?on/.test(text)) {
                return 'Our Self-Adhesive Wallpapers are perfect for DIY installation — just peel and stick! No glue needed. Great for renters and quick makeovers.';
            }

            // Pricing
            if (/price|cost|rate|how much|expensive|cheap|budget/.test(text)) {
                return 'Our prices range from ₹85/sqft for standard wallpapers to ₹3,000/pc for premium murals. Final pricing depends on the design and wall size. Free shipping on orders above ₹5,000!';
            }

            // Shipping & Delivery
            if (/ship|deliver|delivery|how long|when|reach/.test(text)) {
                return 'We deliver across India and internationally! Domestic orders typically arrive in 5-7 business days. International shipping takes 10-15 days. Free shipping on orders above ₹5,000 within India.';
            }

            // Installation
            if (/install|fit|apply|put up|set up|fix/.test(text)) {
                return 'We offer professional installation services in major cities (Mumbai, Delhi, Bangalore, Chennai). For other locations, we provide detailed DIY guides. Would you like to book an installation?';
            }

            // Returns
            if (/return|refund|exchange|replace/.test(text)) {
                return 'We offer easy 7-day returns! If you\'re not happy with your order, contact us within 7 days of delivery for a full refund or exchange.';
            }

            // Contact
            if (/contact|phone|call|email|reach|whatsapp|number/.test(text)) {
                return 'You can reach us at hello@mahashanka.com or +91 98765 43210. We\'re available Monday-Saturday, 10 AM - 7 PM IST. We also respond on WhatsApp!';
            }

            // Rooms
            if (/living room|bedroom|dining|hallway|study|bathroom/.test(text)) {
                return 'Great choice! We have wallpapers curated for every room. Check out our "Browse by Room" section on the homepage for room-specific recommendations!';
            }

            // Color
            if (/color|colour|shade|tone|palette/.test(text)) {
                return 'We offer wallpapers in 5 curated palettes: Warm Neutrals, Earthy Browns, Cool Grays, Soft Blues, and Sage & Greens. What\'s your preferred color scheme?';
            }

            // Size / measurement
            if (/size|measure|dimension|how to measure|square feet|sqft|wall size/.test(text)) {
                return 'To calculate how much wallpaper you need: measure your wall\'s width × height in feet. For patterned wallpapers, add 10-15% extra for pattern matching. Need help? Share your wall dimensions and we\'ll calculate for you!';
            }

            // Order
            if (/order|buy|purchase|checkout|cart/.test(text)) {
                return 'You can place an order directly on our website! Add products to your cart and proceed to checkout. We accept Cash on Delivery and online payments. Need help choosing? I\'m here!';
            }

            // Thanks
            if (/thank|thanks|great|awesome|perfect|nice|cool/.test(text)) {
                return 'You\'re most welcome! 😊 Feel free to browse our collection. If you have any more questions, I\'m always here to help!';
            }

            // Bye
            if (/bye|goodbye|see you|exit|quit/.test(text)) {
                return 'Thank you for visiting Mahashanka! Have a wonderful day. 🙏 Come back anytime!';
            }

            // Default fallback
            return 'I\'d love to help with that! You can ask me about our wallpapers, murals, pricing, shipping, installation, or anything else. For specific queries, you can also email us at hello@mahashanka.com or call +91 98765 43210.';
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
