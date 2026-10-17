"""Independent test bootstrap grants. Never load grants from candidate/source data."""
from ..contracts import ENVIRONMENTS, require
from ..intelligence import SPECIALISTS
from ..tenancy import AuthorizationError

class TestMemoryAccess:
    __test__ = False

    def __init__(self, authority, *, specialists=(), owners=(), test_only=False):
        if test_only is not True:
            raise AuthorizationError('production Memory authorization unavailable')
        self.authority = authority
        self.specialists = {}
        self.owners = {}
        # Exact issued context capabilities, not serializable self-asserted roles.
        for context, specialties, classifications in specialists:
            authority.authorize(context)
            require(bool(specialties) and set(specialties) <= set(SPECIALISTS), 'unknown specialist grant')
            require(set(classifications) <= {'public', 'internal', 'confidential'}, 'invalid access grant')
            self.specialists[id(context)] = (context, tuple(specialties), tuple(classifications))
        for context, partitions, classifications in owners:
            authority.authorize(context, env='personal', roles=('director',))
            require(bool(partitions) and set(partitions) <= set(ENVIRONMENTS[1:]), 'invalid owner partitions')
            require(set(classifications) <= {'public', 'internal', 'confidential'}, 'invalid owner access')
            self.owners[id(context)] = (context, tuple(partitions), tuple(classifications))

    def specialist(self, context, record):
        self.authority.authorize(context, env=record.environment)
        grant = self.specialists.get(id(context))
        if not grant or grant[0] is not context or not set(record.classification.specialists).intersection(grant[1]) or record.packet.classification not in grant[2]:
            raise AuthorizationError('no independent specialist/access grant')

    def owner(self, context, environment, classification=None):
        self.authority.authorize(context, env='personal', roles=('director',))
        grant = self.owners.get(id(context))
        if not grant or grant[0] is not context or environment not in grant[1] or (classification is not None and classification not in grant[2]):
            raise AuthorizationError('independent owner partition/access grant required')
