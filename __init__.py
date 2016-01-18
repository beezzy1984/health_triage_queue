
from trytond.pool import Pool
from .queue import QueueEntry, QueueEntryNote
from .triage import TriageEntry
from .health import Appointment, PatientEncounter
from .wizards import QueueInspectWizard, QueueCallWizard, QueueDismissWizard


def register():
    Pool.register(TriageEntry,
                  QueueEntry,
                  QueueEntryNote,
                  Appointment,
                  PatientEncounter,
                  module='health_triage_queue', type_='model')

    Pool.register(QueueInspectWizard,
                  QueueCallWizard,
                  QueueDismissWizard,
                  module='health_triage_queue', type_='wizard')
