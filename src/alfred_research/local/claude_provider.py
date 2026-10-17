"""Claude-backed Research provider (Anthropic Python SDK).

The API key is read from a private file named in configuration (normally a
systemd ``LoadCredential`` file), never from code, git, or the environment's
value itself. Without a usable key the provider reports "not configured" and
callers fail closed; the extractive worker remains an explicit owner choice.
"""
from dataclasses import dataclass
import json
import os
from pathlib import Path
import stat
import time

from .sources import sha

DEFAULT_RESEARCH_MODEL = 'claude-sonnet-5-5'
DEFAULT_SYNTHESIS_MODEL = 'claude-opus-5-5'
CREDENTIAL_NAME = 'anthropic-api-key'
KEY_FILE_ENV = 'ALFRED_RESEARCH_ANTHROPIC_KEY_FILE'
EFFORTS = ('low', 'medium', 'high', 'xhigh', 'max')
FALLBACK_BETA = 'server-side-fallback-2026-07-01'


class ProviderNotConfigured(RuntimeError):
    """No usable Claude credential or SDK; nothing was sent to a model."""


class ProviderOutputRejected(ValueError):
    """The model answered, but the answer is unusable (refusal, truncation, malformed JSON)."""


@dataclass(frozen=True)
class ClaudeSettings:
    api_key_file: str | None
    research_model: str = DEFAULT_RESEARCH_MODEL
    synthesis_model: str = DEFAULT_SYNTHESIS_MODEL
    research_effort: str = 'medium'
    synthesis_effort: str = 'high'
    fallbacks: bool = True
    timeout_seconds: float = 600.0
    max_investigations: int = 4


def expand(path):
    return path.replace('${CREDENTIALS_DIRECTORY}', os.environ.get('CREDENTIALS_DIRECTORY', ''))


def resolve_settings(config=None):
    """Config dict (Research line ``claude`` block) > key-file env var > systemd credential."""
    config = dict(config or {})
    key_file = config.get('api_key_file') or os.environ.get(KEY_FILE_ENV)
    if not key_file and os.environ.get('CREDENTIALS_DIRECTORY'):
        candidate = Path(os.environ['CREDENTIALS_DIRECTORY']) / CREDENTIAL_NAME
        key_file = str(candidate) if candidate.exists() else None
    settings = ClaudeSettings(
        api_key_file=expand(key_file) if key_file else None,
        research_model=config.get('research_model', DEFAULT_RESEARCH_MODEL),
        synthesis_model=config.get('synthesis_model', DEFAULT_SYNTHESIS_MODEL),
        research_effort=config.get('research_effort', 'medium'),
        synthesis_effort=config.get('synthesis_effort', 'high'),
        fallbacks=config.get('fallbacks', True) is not False,
        timeout_seconds=float(config.get('timeout_seconds', 600)),
        max_investigations=int(config.get('max_investigations', 4)))
    if settings.research_effort not in EFFORTS or settings.synthesis_effort not in EFFORTS:
        raise ValueError('Claude effort must be one of ' + ', '.join(EFFORTS))
    if not 1 <= settings.max_investigations <= 8:
        raise ValueError('max_investigations must be 1-8')
    return settings


def read_key(path):
    # Same private-file rule as the Memory token (systemd credentials are root 0440).
    from .memory import credential_metadata_allowed
    if not path:
        raise ProviderNotConfigured('no API key file configured (set claude.api_key_file or LoadCredential=' + CREDENTIAL_NAME + ')')
    try:
        info = os.stat(path, follow_symlinks=False)
    except OSError:
        raise ProviderNotConfigured('API key file not found: ' + str(path)) from None
    if not stat.S_ISREG(info.st_mode) or not credential_metadata_allowed(info, os.getuid()) or info.st_size > 4096:
        raise ProviderNotConfigured('API key file must be a private regular file (0400/0600, or root 0440 systemd credential)')
    try:
        value = Path(path).read_text().strip()
    except OSError:
        raise ProviderNotConfigured('API key file unreadable') from None
    if not value or any(c.isspace() for c in value):
        raise ProviderNotConfigured('API key file is empty or malformed')
    return value


def status(settings):
    """Configuration check without a network call or exposing the key."""
    try:
        read_key(settings.api_key_file)
        import anthropic  # noqa: F401
    except ProviderNotConfigured as error:
        return {'provider': 'claude', 'configured': False, 'detail': 'Claude provider not configured: ' + str(error)}
    except ImportError:
        return {'provider': 'claude', 'configured': False,
                'detail': 'Claude provider not configured: the anthropic Python package is not installed'}
    return {'provider': 'claude', 'configured': True, 'research_model': settings.research_model,
            'synthesis_model': settings.synthesis_model, 'detail': 'API key file present; no call made'}


class ModelResult(dict):
    """Model JSON plus local execution metadata; never an authoritative attestation."""


class ClaudeProvider:
    def __init__(self, settings, client=None):
        self.settings = settings
        if client is None:
            key = read_key(settings.api_key_file)
            try:
                import anthropic
            except ImportError:
                raise ProviderNotConfigured('the anthropic Python package is not installed') from None
            client = anthropic.Anthropic(api_key=key, timeout=settings.timeout_seconds, max_retries=2)
        self.client = client

    def call_json(self, *, model, effort, system, user, schema, max_tokens=16000):
        request = {'model': model, 'max_tokens': max_tokens, 'system': system,
                   'messages': [{'role': 'user', 'content': user}],
                   'output_config': {'effort': effort, 'format': {'type': 'json_schema', 'schema': schema}}}
        started = time.time()
        try:
            if self.settings.fallbacks:
                response = self.client.beta.messages.create(**request, betas=[FALLBACK_BETA], fallbacks='default')
            else:
                response = self.client.messages.create(**request)
        except Exception as error:
            # SDK errors carry status/request ids, never the key; keep the message short.
            raise RuntimeError('Claude API call failed (' + type(error).__name__ + '): ' + str(error)[:200]) from None
        if response.stop_reason == 'refusal':
            raise ProviderOutputRejected('Claude declined the request; no model output accepted')
        if response.stop_reason == 'max_tokens':
            raise ProviderOutputRejected('Claude output truncated at max_tokens; no model output accepted')
        text = next((block.text for block in response.content if getattr(block, 'type', None) == 'text'), None)
        if text is None or len(text) > 200000:
            raise ProviderOutputRejected('Claude returned no usable JSON text')
        try:
            value = json.loads(text)
        except ValueError:
            raise ProviderOutputRejected('Claude returned malformed JSON') from None
        if not isinstance(value, dict):
            raise ProviderOutputRejected('Claude returned a non-object result')
        result = ModelResult(value)
        usage = getattr(response, 'usage', None)
        result.execution = {
            'provider': 'anthropic-claude', 'requested_model': model, 'model': getattr(response, 'model', model),
            'request_id': getattr(response, '_request_id', None), 'effort': effort,
            'started_at_unix': int(started), 'duration_ms': int((time.time() - started) * 1000),
            'input_tokens': getattr(usage, 'input_tokens', None), 'output_tokens': getattr(usage, 'output_tokens', None),
            'prompt_sha256': sha((system + '\n' + user).encode()), 'output_sha256': sha(text.encode()),
            'simulation': False, 'authority': 'Local execution evidence only'}
        return result
