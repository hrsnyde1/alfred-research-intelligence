"""Personal Alfred -> Research adapter for Hermes' existing post_gateway_admission hook.

Parked for a future release (the dedicated Research line comes first). Prepared,
not installed. Hermes' plugin lifecycle calls ``on_post_gateway_admission(payload)``
with the routed message; returning ``{'action': 'handled', 'reply': text}``
consumes the turn, returning ``None`` leaves it to normal Personal Alfred chat.
Only exact configured owner identities are served, only when explicitly enabled.
Intake, execution, publication and delivery live in ``ResearchDesk``.
"""
import hashlib
import json
import logging
import re

from .desk import ResearchDesk, final_message, short  # noqa: F401  (final_message re-exported)
from .message_intake import detect

log = logging.getLogger(__name__)
HOOK = 'post_gateway_admission'
STATUS_COMMAND = re.compile(r'^\s*(?:alfred[\s,]+)?research (?:status|jobs)(?:\s+(research-[0-9a-f]{32}))?\s*\??\s*$', re.I)


class Owner(tuple):
    """Exact (platform, chat_id, user_id). No wildcards or fallbacks."""
    def __new__(cls, platform, chat_id, user_id):
        values = (platform, chat_id, user_id)
        if any(not isinstance(v, str) or not v.strip() or v != v.strip() or '*' in v for v in values):
            raise ValueError('Owner identity must be exact non-empty strings')
        if chat_id == user_id:
            raise ValueError('Owner user_id must differ from chat_id (Photon sender fallback is not identity)')
        return super().__new__(cls, values)


class HermesResearchAdapter(ResearchDesk):
    def __init__(self, working_directory, owners, *, enabled=False, attachment_roots=(), **options):
        super().__init__(working_directory, **options)
        self.owners = frozenset(Owner(*o) if not isinstance(o, dict) else Owner(o['platform'], o['chat_id'], o['user_id'])
                                for o in owners)
        self.enabled = enabled is True
        self.attachment_roots = tuple(attachment_roots)

    def on_post_gateway_admission(self, payload):
        if not self.enabled or not isinstance(payload, dict):
            return None
        source = payload.get('source') if isinstance(payload.get('source'), dict) else {}
        platform = payload.get('platform') or source.get('platform')
        chat_id, user_id = source.get('chat_id'), source.get('user_id')
        if (platform, chat_id, user_id) not in self.owners:
            return None  # not the owner: Research stays out of the way
        text = payload.get('text') or payload.get('message') or ''
        status = STATUS_COMMAND.match(text) if isinstance(text, str) else None
        if status:
            return self.handled(self.status_reply(status.group(1)))
        intent = detect(text, payload.get('attachments') or payload.get('media') or (), self.attachment_roots)
        if intent is None:
            return None
        message_id = payload.get('message_id')
        if not isinstance(message_id, str) or not message_id.strip() or len(message_id) > 256:
            log.warning('Research intake skipped: host event has no message_id for idempotency')
            return None
        route = {'platform': platform, 'chat_id': chat_id, 'user_id': user_id, 'message_id': message_id,
                 'session_key': payload.get('session_key'), 'profile': source.get('profile'),
                 'environment': 'personal'}
        key = 'hermes:' + hashlib.sha256(json.dumps([platform, chat_id, message_id]).encode()).hexdigest()
        try:
            return self.handled(self.accept(intent, route, key))
        except Exception as error:  # an honest failure beats falling through to an ungrounded chat answer
            log.exception('Research intake failed')
            return self.handled('I couldn\'t start research on that: ' + short(error, 200) + ' Nothing was researched.')

    @staticmethod
    def handled(reply):
        return {'action': 'handled', 'reply': reply}


def register(ctx, config):
    """Plugin entry point. Registers the hook only when ``config['enabled'] is True``.

    ``config``: working_directory, owners [{platform, chat_id, user_id}],
    enabled, provider, attachment_roots, and optionally a ``deliver(route, text)``
    callable bound to Hermes' existing delivery for the original conversation.
    """
    adapter = HermesResearchAdapter(config['working_directory'], config.get('owners', ()),
                                    enabled=config.get('enabled') is True, deliver=config.get('deliver'),
                                    provider=config.get('provider', 'auto'),
                                    attachment_roots=config.get('attachment_roots', ()))
    if not adapter.enabled:
        log.info('Alfred Research hook prepared but disabled; nothing registered')
        return adapter
    ctx.register_hook(HOOK, adapter.on_post_gateway_admission)
    adapter.resume()
    return adapter
