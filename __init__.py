
from trytond.pool import Pool
from .queue import QueueEntry
from .triage import TriageEntry


def register():
    Pool.register(TriageEntry,
                  QueueEntry,
                  module='health_triage_queue', type_='model')
