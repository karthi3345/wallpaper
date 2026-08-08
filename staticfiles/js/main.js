/* Mahashankh — Main JS */

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
        isMinimized: false,
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
                        text: 'Namaste! 🙏 Welcome to Mahashankh! I\'m your AI decor assistant. Ask me about wallpapers, murals, pricing, or how to write great prompts for our AI Generator!'
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

                // If redirected to login (user not authenticated), redirect the page
                if (resp.redirected || resp.status === 302) {
                    window.location.href = '/login/';
                    return;
                }

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

                // If redirected to login (user not authenticated), redirect the page
                if (resp.redirected || resp.status === 302) {
                    window.location.href = '/login/';
                    return;
                }

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
        },

        /**
         * Convert markdown text to safe HTML for bot messages.
         * Uses marked.js if available, falls back to basic formatting.
         * All output is sanitized to prevent XSS.
         */
        renderMarkdown(text) {
            if (!text) return '';

            // Use marked.js if available (loaded from CDN)
            if (typeof marked !== 'undefined') {
                try {
                    marked.setOptions({
                        breaks: true,      // single line breaks → <br>
                        gfm: true,         // GitHub-flavored markdown (tables!)
                        headerIds: false,  // no id attributes on headers
                        mangle: false,
                    });
                    let html = marked.parse(text);
                    return this.sanitizeHtml(html);
                } catch (e) {
                    console.warn('Markdown parse error:', e);
                }
            }

            // Fallback: basic markdown without library
            return this.basicMarkdown(text);
        },

        /**
         * Sanitize HTML output — strip dangerous tags/attributes.
         */
        sanitizeHtml(html) {
            // Remove script, iframe, object, embed, style tags entirely
            html = html.replace(/<\s*(script|iframe|object|embed|style|form|input|button)[^>]*>[\s\S]*?<\s*\/\s*\1\s*>/gi, '');
            html = html.replace(/<\s*(script|iframe|object|embed|style|form|input|button)[^>]*\/?\s*>/gi, '');
            // Remove event handlers (on*)
            html = html.replace(/\son\w+\s*=\s*"[^"]*"/gi, '');
            html = html.replace(/\son\w+\s*=\s*'[^']*'/gi, '');
            html = html.replace(/\son\w+\s*=\s*[^\s>]+/gi, '');
            // Remove javascript: and data: URLs
            html = html.replace(/(href|src)\s*=\s*["']javascript:[^"']*["']/gi, '$1="#"');
            html = html.replace(/(href|src)\s*=\s*["']data:[^"']*["']/gi, '$1="#"');
            // Make links safe
            html = html.replace(/<a\s/g, '<a target="_blank" rel="noopener noreferrer" ');
            return html;
        },

        /**
         * Basic markdown rendering without external library.
         */
        basicMarkdown(text) {
            let html = this.escapeHtml(text);

            // Tables (pipe-delimited)
            html = html.replace(/((?:^\|.+\|[ \t]*$\n?)+)/gm, function(match) {
                var lines = match.trim().split('\n');
                if (lines.length < 2) return match;
                // Check if second line is separator
                if (!/^\|?[\s:|-]+\|?\s*$/.test(lines[1])) return match;

                var headers = lines[0].split('|').filter(function(h) {
                    return h.trim() !== '';
                }).map(function(h) { return h.trim(); });

                var rows = lines.slice(2).map(function(line) {
                    return line.split('|').filter(function(c) {
                        return c.trim() !== '';
                    }).map(function(c) { return c.trim(); });
                });

                var table = '<div class="chat-table-wrap"><table class="chat-md-table"><thead><tr>';
                headers.forEach(function(h) { table += '<th>' + h + '</th>'; });
                table += '</tr></thead><tbody>';
                rows.forEach(function(r) {
                    table += '<tr>';
                    r.forEach(function(c) { table += '<td>' + c + '</td>'; });
                    table += '</tr>';
                });
                table += '</tbody></table></div>';
                return table;
            });

            // Bold
            html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
            // Italic
            html = html.replace(/(?<!\w)\*(?!\s)(.+?)\*(?!\w)/g, '<em>$1</em>');
            // Inline code
            html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
            // Headings (### and ##)
            html = html.replace(/^###\s+(.+)$/gm, '<h4 class="chat-md-h">$1</h4>');
            html = html.replace(/^##\s+(.+)$/gm, '<h4 class="chat-md-h">$1</h4>');
            // Lists — mark items with data-type, then wrap groups
            // Numbered list items
            html = html.replace(/^\d+\.\s+(.+)$/gm, '<li data-t="ol">$1</li>');
            // Bullet list items (only if not already a <li> from numbered)
            html = html.replace(/^[-*]\s+(.+)$/gm, '<li data-t="ul">$1</li>');
            // Wrap consecutive same-type items
            html = html.replace(/(?:<li data-t="ol">.*?<\/li>\n?)+/g, function(m) {
                return '<ol class="chat-md-ol">' + m.replace(/ data-t="ol"/g, '') + '</ol>';
            });
            html = html.replace(/(?:<li data-t="ul">.*?<\/li>\n?)+/g, function(m) {
                return '<ul class="chat-md-ul">' + m.replace(/ data-t="ul"/g, '') + '</ul>';
            });
            html = html.replace(/<li>/g, '<li class="chat-md-li">');
            // Line breaks
            html = html.replace(/\n/g, '<br>');
            return html;
        },

        /**
         * Escape HTML entities — used for user messages and as base for markdown.
         */
        escapeHtml(text) {
            var div = document.createElement('div');
            div.appendChild(document.createTextNode(text));
            return div.innerHTML;
        }
    };
}
