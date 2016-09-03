
from trytond.pool import Pool
from .queue import QueueEntry, QueueEntryNote
from .triage import TriageEntry, TriageNote
from .health import Appointment, PatientEncounter
from .referral import PatientReferral
from .wizards import (QueueInspectWizard, QueueCallWizard, QueueDismissWizard,
                      AppointmentSetup, QueueAppointmentWizard,
                      TriageReferWizard)


def register():
    Pool.register(TriageEntry,
                  TriageNote,
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
                  TriageReferWizard,
                  module='health_triage_queue', type_='wizard')
