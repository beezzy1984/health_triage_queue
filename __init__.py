
from trytond.pool import Pool
from .queue import QueueEntry, QueueEntryNote
from .triage import TriageEntry
from .health import Appointment, PatientEncounter
from .referral import PatientReferral
from .wizards import (QueueInspectWizard, QueueCallWizard, QueueDismissWizard,
                      AppointmentSetup, QueueAppointmentWizard)


def register():
    Pool.register(TriageEntry,
                  QueueEntry,
                  QueueEntryNote,
                  Appointment,
                  PatientEncounter,
                  AppointmentSetup,
                  PatientReferral,
                  module='health_triage_queue', type_='model')

    Pool.register(QueueInspectWizard,
                  QueueCallWizard,
                  QueueDismissWizard,
                  QueueAppointmentWizard,
                  module='health_triage_queue', type_='wizard')
