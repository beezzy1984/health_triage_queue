
from trytond.wizard import (Wizard, StateAction, StateTransition, StateView,
                            Button)
from trytond.transaction import Transaction
from trytond.model import ModelView, fields
from trytond.pool import Pool
from trytond.pyson import PYSONEncoder, Eval
from datetime import datetime, timedelta


class OneQItemWizard(Wizard):

    def __init__(self, sessionid):
        super(OneQItemWizard, self).__init__(sessionid)
        tact = Transaction()
        active_id = tact.context.get('active_id')
        q_model = Pool().get('gnuhealth.patient.queue_entry')
        try:
            qentry = q_model.browse([active_id])[0]
        except IndexError:
            self.raise_user_error('no_record_selected')
        self._qdata = {'active_id': active_id, 'obj': qentry, 'model':q_model}

    @classmethod
    def __setup__(cls):
        super(OneQItemWizard, cls).__setup__()
        cls._error_messages.update({
            'no_record_selected': 'You need to select a queue entry',
        })

    def _touch_busy_flag(self, flag=False):
        model = self._qdata['model']
        model.write([self._qdata['obj']], {'busy': flag})

    def set_entry_busy(self):
        'sets the busy flag on the currently selected queue entry items'
        self._touch_busy_flag(True)

    def unset_entry_busy(self):
        'unsets the busy flag on the currently selected queue entry items'
        self._touch_busy_flag(False)


class OneTriageWizard(Wizard):

    def __init__(self, sessionid):
        super(OneTriageWizard, self).__init__(sessionid)
        tact = Transaction()
        active_id = tact.context.get('active_id')
        triage_model = Pool().get('gnuhealth.triage.entry')
        try:
            entry = triage_model.browse([active_id])[0]
        except IndexError:
            self.raise_user_error('no_record_selected')
        self._xdata = {'active_id': active_id, 'obj': entry,
                       'model': triage_model}


class QueueInspectWizard(OneQItemWizard):
    'Queue Item Peek/Inspect Wizard'
    __name__ = 'gnuhealth.queue_entry.inspect_wizard'

    start = StateTransition()
    goto_encounter = StateAction('health_encounter.actwin_appt_encounter')
    goto_appointment = StateAction(
        'health_triage_queue.actwin_queue_appointment')
    goto_triage = StateAction('health_triage_queue.actwin_queue_triage')

    def transition_start(self):
        'Decide which state to hit next.'
        qentry = self._qdata['obj']
        if qentry.encounter:
            return 'goto_encounter'
        elif qentry.appointment:
            return 'goto_appointment'
        else:
            return 'goto_triage'

    def do_goto_encounter(self, action):
        'Launch the existing encounter'
        qentry = self._qdata['obj']
        rd = {'active_id': qentry.encounter.id}
        action['res_id'] = rd['active_id']

        return action, rd

    def do_goto_appointment(self, action):
        'Launch the existing appointment'
        qentry = self._qdata['obj']
        rd = {'active_id': qentry.appointment.id}
        action['res_id'] = rd['active_id']

        return action, rd

    def do_goto_triage(self, action):
        'Launch the existing triage entry'
        qentry = self._qdata['obj']
        rd = {'active_id': qentry.triage_entry.id}
        action['res_id'] = rd['active_id']

        return action, rd


class QueueCallWizard(QueueInspectWizard):
    'Queue Item Call Wizard'
    __name__ = 'gnuhealth.queue_entry.call_wizard'

    def transition_start(self):
        next_state = super(QueueCallWizard, self).transition_start()
        # set the queue entry busy
        self.set_entry_busy()
        return next_state


class QueueDismissWizard(OneQItemWizard):
    '''Queue Item Dismiss
    Wizard called to dismiss a queue entry or release a patient'''
    __name__ = 'gnuhealth.queue_entry.dismiss_wizard'

    start = StateTransition()

    def transition_start(self):
        next_state = 'end'
        self.unset_entry_busy()
        return next_state


def now_treshold():
    delta = timedelta(0, 60 * 60 * 3)  # 3 hours
    return datetime.now() + delta


class AppointmentSetup(ModelView):
    'Setup Appointment'
    __name__ = 'gnuhealth.queue_entry.appointment_setup'

    has_patient = fields.Boolean('Patient tied to queue entry?')
    patient = fields.Many2One(
        'gnuhealth.patient', 'Patient', help="Find or create patient",
        required=True, states={'readonly': Eval('has_patient', False)})
    make_new = fields.Boolean('Create new appointment')
    appointment = fields.Many2One('gnuhealth.appointment',
                                  'Select Appointment',
                                  domain=[('state', '=', 'free')],
                                  states={'invisible': Eval('make_new', False)})
    appointment_time = fields.DateTime(
        'Date and Time', help='Select Date and time for appointment',
        states={'required': Eval('make_new', False)})
    specialty = fields.Many2One(
        'gnuhealth.specialty', 'Specialty',
        help='Medical Specialty / Sector',
        states={'invisible': ~Eval('make_new', False),
                'required': Eval('make_new', False)})
    urgency = fields.Selection([
        (None, ''),
        ('a', 'Normal'),
        ('b', 'Urgent'),
        ('c', 'Medical Emergency'),
        ], 'Appointment Urgency', sort=False)  #,
        # states={'invisible': ~Eval('make_new', False),
        #         'required': Eval('make_new', False)})
    appointment_arrived = fields.Boolean(
        'Mark as Arrived/Waiting',
        help='Check to mark the assigned appointment as Arrived/Waiting')

    @fields.depends('appointment')
    def on_change_appointment(self):
        if self.appointment:
            return {'appointment_time': self.appointment.appointment_date,
                    'urgency': self.appointment.urgency}
        return {}

    @fields.depends('appointment_time')
    def on_change_appointment_time(self):
        if self.appointment_time and self.appointment_time < now_treshold():
            return {'appointment_arrived': True}
        return {'appointment_arrived': False}


class QueueAppointmentWizard(OneQItemWizard):
    '''Create Appointment
    This wizard creates an appointment from a triage entry in the
    "registration" state.
    '''
    __name__ = 'gnuhealth.queue_entry.appointment_setup_wizard'
    start = StateTransition()
    setup_start = StateView(
        'gnuhealth.queue_entry.appointment_setup',
        'health_triage_queue.health_view_queue_appt_wiz0',
        [Button('Cancel', 'end', 'tryton-cancel'),
         Button('Ok', 'setup_finish', 'tryton-ok', default=True)])
    setup_finish = StateTransition()

    def transition_start(self):
        qentry = self._qdata['obj']
        if qentry.appointment or qentry.encounter:
            # there's already an appointment here. nothing to do
            return 'end'
        else:
            triage_entry = qentry.triage_entry
            if triage_entry and triage_entry.patient:
                # patient tied to the triage_entry
                self._qdata['patient'] = triage_entry.patient
                self._qdata['appt_urgency'] = 'a'
                if triage_entry.priority in '12':
                    self._qdata['appt_urgency'] = 'c'
                elif triage_entry.priority in '3':
                    self._qdata['appt_urgency'] = 'b'
            return 'setup_start'

    def default_setup_start(self, fields):
        '''return default values for the setup-start state of the wizard'''
        qdata = self._qdata
        qitem = qdata['obj']
        if 'patient' in qdata:
            outd = {'has_patient': True, 'patient': int(qdata['patient'])}
        else:
            outd = {'has_patient': False}
        if 'appt_urgency' in qdata:
            outd['urgency'] = qdata['appt_urgency']
        return outd

    def transition_setup_finish(self):
        starter = self.setup_start
        pool = Pool()
        appt_model = pool.get('gnuhealth.appointment')
        queue_model = pool.get('gnuhealth.patient.queue_entry')
        qentry = self._qdata['obj']
        appt_data = {'state': 'confirmed', 'patient': starter.patient.id,
                     # 'speciality': starter.specialty,
                     'urgency': starter.urgency, 'healthprof': None}
        if starter.make_new:
            # create new appointment in scheduled state with patient, urgency and date
            appt_data.update({'appointment_date': starter.appointment_time,
                              'speciality': starter.specialty})
            appointment, = appt_model.create([appt_data])
            # save queue entry
        else:  # existing appointment to be modified
            appointment = starter.appointment
            appt_model.write([appointment], appt_data)

        # attach patient to triage entry if not previously attached:
        triage = qentry.triage_entry
        if triage:
            if not starter.has_patient:
                triage.patient = starter.patient
            triage.status = 'done'
            triage.save()
        if starter.appointment_arrived:
            # attach appointment to queue entry
            queue_model.write([qentry], {'appointment': appointment})
            # set appointment to arrived
            appt_model.write([appointment], {'state': 'arrived'})
        return 'end'

