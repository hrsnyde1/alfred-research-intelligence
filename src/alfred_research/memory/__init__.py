"""Test-only Memory ports and protected HQ simulations; no live adapter."""
from .contracts import KnowledgeCandidate, MemoryCommand, MemoryReceipt, RetrievalResult, MemoryPort
from .access import TestMemoryAccess
from .fake import FakeMemoryAdapter, DeliveryAmbiguous
