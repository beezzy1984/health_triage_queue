
from trytond.wizard import (Wizard, StateAction, StateTransition)
from trytond.transaction import Transaction
from trytond.pool import Pool
from trytond.pyson import PYSONEncoder


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
            'no_record_selected': 'You need to select an queue entry',
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
