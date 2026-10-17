"""Research-only offline integration; production messaging remains absent."""
from .contracts import Conversation, ResearchMessage, FlowOptions, FlowResult, Notice
from .notifications import ConversationRegistry, FakeConversationTransport, Notifications
from .coordinator import ResearchWorkflow
