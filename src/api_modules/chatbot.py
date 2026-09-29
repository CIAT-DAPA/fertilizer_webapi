"""Server-side chatbot endpoint (OpenAI proxy).

The browser never talks to OpenAI directly. The API key, the model and the
system prompt all live here, so nothing secret is ever shipped inside the
React bundle. The frontend only sends the user's message plus the small
amount of conversation state the prompt needs.
"""

import json
import logging
import re
import threading
import time
from collections import deque

import requests
from flask import request
from flask_restful import Resource

from conf import config

logger = logging.getLogger(__name__)

OPENAI_CHAT_COMPLETIONS_URL = 'https://api.openai.com/v1/chat/completions'

# Input guards (characters / items). Generous for real use, tight enough to
# stop someone pushing huge prompts through the key.
MAX_MESSAGE_CHARS = 4000
MAX_CONTEXT_CHARS = 16000
MAX_CROPS = 100
MAX_CROP_NAME_CHARS = 60
MAX_COLLECTED_DATA_CHARS = 2000

FALLBACK_REPLY = {
    'extracted_data': {},
    'missing_data': [],
    'next_action': 'collect_data',
}


# --------------------------------------------------------------------------- #
# Rate limiting: tiny in-memory sliding window, per client IP, per process.
# --------------------------------------------------------------------------- #
class _RateLimiter:

    def __init__(self, window_seconds=60):
        self.window = window_seconds
        self._hits = {}
        self._lock = threading.Lock()

    def allow(self, key, limit):
        if limit <= 0:
            return True
        now = time.monotonic()
        with self._lock:
            hits = self._hits.setdefault(key, deque())
            while hits and now - hits[0] > self.window:
                hits.popleft()
            if len(hits) >= limit:
                return False
            hits.append(now)
            if len(self._hits) > 5000:
                stale = [k for k, v in self._hits.items()
                         if not v or now - v[-1] > self.window]
                for k in stale:
                    self._hits.pop(k, None)
            return True

    def reset(self):
        with self._lock:
            self._hits.clear()


_rate_limiter = _RateLimiter()


def reset_rate_limiter():
    """Used by unit tests."""
    _rate_limiter.reset()


def _client_ip():
    forwarded = request.headers.get('X-Forwarded-For', '')
    if forwarded:
        return forwarded.split(',')[0].strip() or 'unknown'
    return request.remote_addr or 'unknown'


def _error(status, code, message):
    return {'error': {'code': code, 'message': message}}, status


# --------------------------------------------------------------------------- #
# System prompt (moved verbatim from the React app so behaviour is unchanged).
# --------------------------------------------------------------------------- #
def build_system_prompt(crops, collected_data, session_complete):
    crops = list(crops or [])
    crops_text = ', '.join(crops)
    crops_examples = ', '.join(crops[:3]) + (', and more' if len(crops) > 3 else '')
    session_status = (
        'PREVIOUS_ADVISORY_COMPLETE — do not re-trigger recommendation from chat history alone'
        if session_complete else 'COLLECTING_OR_NEW'
    )
    # Match JavaScript's JSON.stringify(): compact separators, unicode kept.
    collected_json = json.dumps(collected_data or {}, separators=(',', ':'), ensure_ascii=False)

    return (
        "You are an expert in site-specific fertilizer recommendation for Ethiopian farmers. Your goal is to collect exactly 3 pieces of information, then the system fetches data and builds the final recommendation message.\n"
        "\n"
        "REQUIRED INFORMATION (collect intelligently — ask only for what is still missing):\n"
        "1. Crop type\n"
        "2. Farm size in hectares (ha)\n"
        "3. Location coordinates in Ethiopia\n"
        "\n"
        "DO NOT ask the user to choose a fertilizer type. The system selects products automatically when it delivers the final recommendation.\n"
        "\n"
        "CRITICAL — PRODUCT NAMES IN CONVERSATION:\n"
        "- While collecting information or chatting, NEVER mention specific fertilizer product names (DAP, Urea, NPS, compost, etc.). Use only general terms: \"fertilizer\", \"fertilizer recommendations\", \"fertilizer amounts\".\n"
        "- The system builds the final message with specific products and kg amounts; you do not repeat those names before that step.\n"
        "- ONLY if the user explicitly asks what fertilizer types are available (e.g. \"which fertilizers do you recommend?\"), you may say this advisor provides site-specific DAP and Urea amounts plus expected yield.\n"
        "- If the user names a product while requesting advice, acknowledge their request in general terms (e.g. \"I'll get fertilizer recommendations for your crop\") without repeating product names unless they asked what is available.\n"
        "\n"
        "CRITICAL: You MUST NEVER invent fertilizer amounts, yield values, or totals. The system fetches kg/ha from the API and multiplies by farm size. You only collect missing fields and converse naturally.\n"
        "\n"
        "Available crops: " + crops_text + "\n"
        "\n"
        "When the user gives farm size, extract a numeric hectares value (e.g. \"2 ha\", \"1.5 hectares\", \"farm is 3ha\"). Store as a number in farm_size_ha.\n"
        "\n"
        "CRITICAL — INTENT GATING FOR next_action \"get_recommendation\":\n"
        "- Set next_action to \"get_recommendation\" ONLY when (a) crop, farm_size_ha, and coordinates are all known, AND (b) the user's LATEST message clearly asks for fertilizer amounts / a recommendation / to check a location or crop.\n"
        "- NEVER set get_recommendation for: how to apply fertilizer, application timing/strategy, greetings, thanks, \"ok\", \"leave it\", cancel, or vague acknowledgments.\n"
        "- NEVER re-use a previous completed advisory to run another recommendation unless the user explicitly asks for another crop/location/recommendation.\n"
        "- If the latest user message is only acknowledging or abandoning a prior result (\"ok\", \"leave it\", \"thanks\"), set next_action to \"collect_data\", keep extracted_data fields null, and reply briefly without re-running advice.\n"
        "- Session status: " + session_status + "\n"
        "\n"
        "When all three fields are present (crop, farm_size_ha, coordinates) AND the user is clearly requesting rates/recommendation, set next_action to \"get_recommendation\". Do not ask for fertilizer type.\n"
        "\n"
        "LANGUAGE TONE: Clear, professional, agriculture-appropriate. Avoid words like \"thrilled\", \"fantastic\", or \"amazing\".\n"
        "\n"
        "Current collected data: " + collected_json + "\n"
        "\n"
        "CRITICAL: Respond with ONLY ONE valid JSON object:\n"
        "\n"
        "{\"response\":\"Your conversational response\",\"extracted_data\":{\"crop\":\"extracted crop or null\",\"coordinates\":\"lat,lon or null\",\"farm_size_ha\":number or null},\"missing_data\":[\"crop\",\"farm_size_ha\",\"coordinates\"],\"next_action\":\"collect_data|get_recommendation|show_map\"}\n"
        "\n"
        "SPECIAL INSTRUCTIONS FOR \"HOW DOES THE BOT WORK?\":\n"
        "If the user asks how the bot works, explain:\n"
        "\n"
        "\"I provide site-specific fertilizer recommendations and expected yield for your farm. I need three things:\n"
        "\n"
        "\U0001F33E Crop — e.g. " + crops_examples + "\n"
        "\U0001F4D0 Farm size — your area in hectares (ha)\n"
        "\U0001F4CD Location — GPS at your field is used automatically when allowed; map or typed coordinates are fallbacks only\n"
        "\n"
        "I'll calculate fertilizer amounts for your whole farm and your expected harvest. Specific products and kg totals appear in the final recommendation.\"\n"
        "\n"
        "You may also mention they can tap \"How to apply fertilizer?\" for the full split-application strategy under uncertain rainfall.\n"
        "\n"
        "IMPORTANT: Before triggering a recommendation, ensure intent is clear. Greetings, how-to-apply questions, and off-topic messages should get a friendly redirect, not next_action get_recommendation.\n"
        "\n"
        "SPECIAL INSTRUCTIONS FOR HOW TO APPLY / APPLICATION STRATEGY:\n"
        "If the user asks how to apply fertilizer, \"how to apply?\", application timing/steps, or split urea under rainfall uncertainty: do NOT set get_recommendation, and do NOT tell them to tap or select a button. Reply briefly that you will show the full application strategy (the app displays it automatically). Keep extracted_data null unless they are also starting a new rates request.\n"
        "\n"
        "SPECIAL INSTRUCTIONS FOR COORDINATES:\n"
        "- DEFAULT: The app uses phone GPS automatically when the user asks for advice or taps a \"for my location\" quick button. collected_data.coordinates may already be set — never ask for location again if it is set.\n"
        "- If coordinates are missing, tell the user to allow GPS when the browser prompts them. Do NOT lead with the map.\n"
        "- FALLBACK ONLY: Mention the map or typing latitude,longitude only if GPS is unavailable or the user explicitly asks for the map or manual coordinates.\n"
        "- Set next_action to \"show_map\" ONLY when the user explicitly wants the map (e.g. \"show map\", \"use map\", \"pick on map\") — not as the default way to get location.\n"
        "- When next_action is collect_data and location is still missing, remind them GPS is tried automatically; map/coordinates are backup options.\n"
        "\n"
        "If the user asks for explainability—such as \"Why did you recommend this?\" or any similar questions about the reasoning behind the recommendation—respond with an intelligent explanation like the following:\n"
        "\n"
        "\"The recommended fertilizer value is derived from your location's specific soil properties, climate conditions, and topographic features, along with the crop's nutrient requirements. These recommendations are generated by a machine learning model that analyzes multiple environmental and agronomic factors.\n"
        "\n"
        "At the moment, I don't have access to the full dataset needed to provide a more detailed breakdown. Once my developer grants access to the complete data, I'll be able to offer a more in-depth explanation.\"\n"
        "\n"
        "Then, continue the conversation in a helpful and engaging manner with statements such as:\n"
        "\n"
        "\"If you have any more questions or need assistance, I'm here to help\"\n"
        "\n"
        "If user provides coordinates, extract them in format \"lat,lon\". Valid Ethiopia coordinates: latitude 3.4-14.9, longitude 33.0-48.0.\n"
        "\n"
        "If user asks about other topics, provide general responses and redirect to fertilizer recommendations."
    )


# --------------------------------------------------------------------------- #
# Response parsing (same tolerant logic the React app used).
# --------------------------------------------------------------------------- #
def parse_assistant_content(content):
    text = (content or '').strip()
    start = text.find('{')
    end = text.rfind('}')
    candidate = text[start:end + 1] if start != -1 and end > start else text
    try:
        parsed = json.loads(candidate)
        if isinstance(parsed, dict):
            reply = dict(FALLBACK_REPLY)
            reply.update(parsed)
            if not isinstance(reply.get('extracted_data'), dict):
                reply['extracted_data'] = {}
            if not isinstance(reply.get('missing_data'), list):
                reply['missing_data'] = []
            reply['response'] = str(reply.get('response') or '')
            return reply
    except (ValueError, TypeError):
        pass
    match = re.search(r'"response":"([^"]+)"', text)
    reply = dict(FALLBACK_REPLY)
    reply['response'] = match.group(1) if match else text
    return reply


def _upstream_error_message(payload):
    if isinstance(payload, dict):
        err = payload.get('error')
        if isinstance(err, dict) and err.get('message'):
            return str(err['message'])
        if isinstance(err, str):
            return err
    return ''


def _validate_payload(payload):
    """Returns (clean_payload, error_tuple_or_None)."""
    if not isinstance(payload, dict):
        return None, _error(400, 'invalid_request', 'JSON body expected.')

    message = payload.get('message')
    if not isinstance(message, str) or not message.strip():
        return None, _error(400, 'invalid_request', "'message' is required.")
    if len(message) > MAX_MESSAGE_CHARS:
        return None, _error(400, 'invalid_request',
                            "'message' is too long (max %d characters)." % MAX_MESSAGE_CHARS)

    context = payload.get('conversation_context') or ''
    if not isinstance(context, str):
        return None, _error(400, 'invalid_request', "'conversation_context' must be a string.")
    if len(context) > MAX_CONTEXT_CHARS:
        # Keep the most recent part of the conversation.
        context = context[-MAX_CONTEXT_CHARS:]

    crops = payload.get('crops') or []
    if not isinstance(crops, list):
        return None, _error(400, 'invalid_request', "'crops' must be a list of strings.")
    crops = [str(c)[:MAX_CROP_NAME_CHARS] for c in crops[:MAX_CROPS] if isinstance(c, (str, int, float))]

    collected = payload.get('collected_data')
    if collected is None:
        collected = {}
    if not isinstance(collected, dict):
        return None, _error(400, 'invalid_request', "'collected_data' must be an object.")
    if len(json.dumps(collected, ensure_ascii=False)) > MAX_COLLECTED_DATA_CHARS:
        return None, _error(400, 'invalid_request', "'collected_data' is too large.")

    session_complete = bool(payload.get('session_complete', False))

    return {
        'message': message,
        'conversation_context': context,
        'crops': crops,
        'collected_data': collected,
        'session_complete': session_complete,
    }, None


class ChatbotMessage(Resource):

    def __init__(self):
        super().__init__()

    def post(self):
        """
        Chatbot: send a user message to the fertilizer advisory assistant (server-side OpenAI proxy).
        ---
        description: Forwards one chatbot turn to the LLM. The OpenAI API key, model and system prompt are held on the server, so the browser never needs a key. Returns the assistant's structured reply (response text, extracted fields, missing fields, next action). Rate limited per client IP.
        consumes:
          - application/json
        parameters:
          - in: body
            name: body
            required: true
            schema:
              id: ChatbotRequest
              required:
                - message
              properties:
                message:
                  type: string
                  description: The latest user message.
                  example: I grow wheat on 2 ha near Bahir Dar, what should I apply?
                conversation_context:
                  type: string
                  description: Recent conversation transcript (optional).
                collected_data:
                  type: object
                  description: Fields already collected, e.g. {"crop":"wheat","coordinates":null,"farmSizeHa":2}
                crops:
                  type: array
                  items:
                    type: string
                  description: Crop names currently available in the app.
                session_complete:
                  type: boolean
                  description: True when a previous advisory has already been delivered in this session.
        responses:
          200:
            description: Structured assistant reply
            schema:
              id: ChatbotReply
              properties:
                response:
                  type: string
                extracted_data:
                  type: object
                missing_data:
                  type: array
                  items:
                    type: string
                next_action:
                  type: string
                  example: collect_data
          400:
            description: Invalid request body
          429:
            description: Too many requests (client rate limit or upstream rate limit)
          502:
            description: Upstream LLM error
          503:
            description: LLM not configured on the server
          504:
            description: Upstream LLM timeout
        """
        api_key = config.get('OPENAI_API_KEY') or ''
        if not api_key:
            logger.error('Chatbot request received but OPENAI_API_KEY is not configured.')
            return _error(503, 'llm_not_configured',
                          'The AI assistant is not configured on the server.')

        if not _rate_limiter.allow(_client_ip(), int(config.get('CHATBOT_RATE_LIMIT_PER_MINUTE') or 0)):
            return _error(429, 'rate_limited',
                          'Too many requests. Please wait a moment and try again.')

        clean, err = _validate_payload(request.get_json(silent=True))
        if err:
            return err

        system_prompt = build_system_prompt(
            clean['crops'], clean['collected_data'], clean['session_complete'])

        body = {
            'model': config.get('OPENAI_CHAT_MODEL') or 'gpt-4o-mini',
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user',
                 'content': clean['conversation_context'] + '\n\nUser: ' + clean['message']},
            ],
            'temperature': 0.7,
            'max_tokens': 1024,
            'response_format': {'type': 'json_object'},
        }

        try:
            upstream = requests.post(
                OPENAI_CHAT_COMPLETIONS_URL,
                headers={
                    'Authorization': 'Bearer ' + api_key,
                    'Content-Type': 'application/json',
                },
                json=body,
                timeout=config.get('OPENAI_TIMEOUT_SECONDS') or 45,
            )
        except requests.Timeout:
            logger.warning('OpenAI request timed out.')
            return _error(504, 'upstream_timeout', 'The AI service took too long to respond.')
        except requests.RequestException as exc:
            logger.error('OpenAI request failed: %s', exc)
            return _error(502, 'upstream_unreachable', 'Could not reach the AI service.')

        try:
            data = upstream.json()
        except ValueError:
            data = {}

        if upstream.status_code != 200:
            detail = _upstream_error_message(data) or ('HTTP %s' % upstream.status_code)
            logger.error('OpenAI error %s: %s', upstream.status_code, detail)
            if upstream.status_code == 429:
                return _error(429, 'upstream_rate_limited', detail)
            return _error(502, 'upstream_error', detail)

        try:
            content = data['choices'][0]['message']['content']
        except (KeyError, IndexError, TypeError):
            logger.error('Unexpected OpenAI response structure.')
            return _error(502, 'upstream_error', 'Unexpected response from the AI service.')

        return parse_assistant_content(content)
