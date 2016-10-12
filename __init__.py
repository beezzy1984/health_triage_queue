
from trytond.pool import Pool
from .queue import QueueEntry, QueueEntryNote, QueueCallLog
from .triage import TriageEntry, TriageNote
from .health import Appointment, PatientEncounter
from .referral import PatientReferral
from .wizards import (QueueInspectWizard, QueueCallWizard, QueueDismissWizard,
                      AppointmentSetup, QueueAppointmentWizard,
                      TriageReferWizard)
from .reports import TriageReport


def register():
    """Registers classes to tryton's pool"""
    Pool.register(TriageEntry,
                  TriageNote,
                  QueueEntry,
                  QueueEntryNote,
                  QueueCallLog,
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

    Pool.register(
        TriageReport,
        module='health_triage_queue', type_='report')
