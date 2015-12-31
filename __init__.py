
from trytond.pool import Pool
from .queue import QueueEntry
from .triage import TriageEntry
from .wizards import QueueInspectWizard, QueueCallWizard, QueueDismissWizard


def register():
    Pool.register(TriageEntry,
                  QueueEntry,
                  module='health_triage_queue', type_='model')

    Pool.register(QueueInspectWizard,
                  QueueCallWizard,
                  QueueDismissWizard,
                  module='health_triage_queue', type_='wizard')
