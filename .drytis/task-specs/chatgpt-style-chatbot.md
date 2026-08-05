# Task: ChatGPT-Style Mistral Chatbot with Markdown Rendering

## Goal
Upgrade the existing Mahashank Decor AI chatbot (powered by Mistral) so that responses render like ChatGPT — with **bold text**, **bullet/numbered lists**, **markdown tables**, and clean paragraph formatting. The bot should intelligently use tables when comparing items (products, features, pricing) and structured formatting for detailed decor guidance.

## Files to Change
1. `shop/decor_assistant.py` — Enhance system prompt to instruct Mistral to format responses with rich markdown
2. `templates/partials/_chatbot.html` — Switch from `x-text` to `x-html` with markdown rendering
3. `static/js/main.js` — Add markdown-to-HTML conversion for bot responses
4. `static/css/custom.css` — Style markdown elements (tables, lists, bold, code) inside chat bubbles

## Acceptance Criteria

### System Prompt Enhancement
- [ ] System prompt instructs Mistral to use **markdown formatting** — bold, lists, tables
- [ ] Prompt instructs when to use tables (comparisons, pricing, features, product info)
- [ ] Prompt instructs when to use lists (step-by-step guides, recommendations)
- [ ] Prompt gives examples of good formatted responses
- [ ] Prompt keeps responses appropriate for a chat bubble (not overly long)

### Markdown Rendering
- [ ] Bot messages render as HTML via a lightweight markdown parser
- [ ] Tables render with proper styling (headers, borders, alternating rows)
- [ ] Bold (**text**) renders as bold
- [ ] Bullet lists (- or *) render as `<ul>`
- [ ] Numbered lists (1.) render as `<ol>`
- [ ] Inline code (`code`) renders as styled `<code>`
- [ ] Line breaks and paragraphs render correctly
- [ ] User messages remain plain text (no markdown rendering for user input)

### CSS Styling
- [ ] Tables inside chat bubbles: compact, scrollable if wide, styled headers
- [ ] Lists: proper indentation, bullet/number markers
- [ ] Bold: bold weight
- [ ] Code: monospace, subtle background
- [ ] All elements respect the brown/cream theme (#4A341D, #C5A55A, #F7F3EF)
- [ ] Mobile responsive

### Safety
- [ ] Markdown rendering sanitizes HTML to prevent XSS (no raw `<script>`, `<iframe>`, etc.)
- [ ] Only the bot responses are rendered as HTML; user input is always escaped
- [ ] Links in responses are safe (target=_blank, rel=noopener)

## Edge Cases
- Very wide tables should scroll horizontally within the bubble
- Long responses should not break the chat window layout
- Empty or error responses should still display cleanly
