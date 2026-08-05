# Spec: Mistral AI Decor Assistant Chatbot

## Goal
Upgrade the existing rule-based chatbot widget to use **Mistral AI** for intelligent,
context-aware responses about the decor store — including product info, pricing,
shipping, installation, and especially **how to write positive & negative prompts**
for the AI Wallpaper Generator.

## Backend changes

### `shop/decor_assistant.py` (NEW)
Mistral-powered chat service:
- Reads `MISTRAL_API_KEY` and `MISTRAL_BASE_URL` from env
- System prompt with full store knowledge (products, categories, pricing, shipping,
  installation, returns, AI generator prompts, rooms, colors)
- `get_ai_response(user_message, conversation_history)` → returns string reply
- Graceful fallback to a helpful message if the API key is missing or the call fails
- Timeout = 30s; never blocks the UI

### `views.py` — `ai_chat(request)` (NEW endpoint)
- POST endpoint returning JSON `{ "reply": "..." }`
- Accepts `{ "message": "...", "history": [...] }`
- Calls `decor_assistant.get_ai_response()`
- Falls back to the old keyword-based reply on API failure
- CSRF protected

### `urls.py`
- Add `path('ai-chat/', views.ai_chat, name='ai_chat')`

## Frontend changes

### `static/js/main.js` — `chatbot()`
- `sendMessage()` and `sendQuickReply()` now POST to `/ai-chat/` via `fetch()`
- Send conversation history (last 6 messages) for context
- Show typing indicator while waiting
- On API error, show a friendly fallback message

### `templates/partials/_chatbot.html`
- Add an "AI-Powered" badge near the header

## Env keys (via backend tool)
- `MISTRAL_API_KEY` — the user-provided key (is_secret=True)
- `MISTRAL_BASE_URL` — `https://api.mistral.ai/v1` (static)
- `MISTRAL_MODEL` — `mistral-large-latest` (static)

## Acceptance criteria
- [ ] Mistral API key saved via env key tool (NOT hardcoded in source)
- [ ] `/ai-chat/` endpoint returns intelligent AI responses
- [ ] Chatbot frontend calls `/ai-chat/` instead of hardcoded getReply()
- [ ] Asking about positive/negative prompts gives helpful AI guidance
- [ ] Asking about products/pricing/shipping gives accurate store info
- [ ] Graceful fallback when Mistral API is unavailable
- [ ] Typing indicator shows while waiting for response
- [ ] No hardcoded API keys or secrets in source code
- [ ] Conversation history (last 6 msgs) sent for context
- [ ] Existing quick-reply buttons still work
