"""Fixed assignment policy; integer synthetic resource/cost units only."""
from .contracts import ModelAssignment, require
from .tenancy import AuthorizationError


class EscalationRequired(AuthorizationError):
    pass


class ModelConfiguration:
    def __init__(self, assignments=(), *, production=False):
        require(type(production) is bool, 'production flag must be boolean')
        self.production = production
        self._assignments = {}
        for assignment in assignments:
            require(type(assignment) is ModelAssignment, 'model assignment required')
            key = (assignment.environment, assignment.specialist)
            require(key not in self._assignments, 'ambiguous model assignment')
            if production and not assignment.approved:
                raise EscalationRequired('production requires explicitly approved assignments')
            self._assignments[key] = assignment

    def resolve(self, env, specialist, provider, model):
        assignment = self._assignments.get((env, specialist))
        if assignment is None or (assignment.provider, assignment.model) != (provider, model):
            raise EscalationRequired('missing assignment or model substitution; owner escalation required')
        if self.production:
            # Host identity/approval integration has not been implemented.
            raise EscalationRequired('production execution disabled pending Linux integration')
        return assignment
