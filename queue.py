
from trytond.pool import Pool
from trytond.model import ModelView, ModelSQL, fields
from trytond.pyson import Eval, Not, Equal, Or, Greater, In, Len

APPOINTMENT_STATES = [
    ('0', ''),
    ('1', 'Triage'),
    ('2', 'Registration'),
    ('3', 'Nurse/Pre-Evaluation'),
    ('4', 'Evaluation'),
    ('99', 'Done'),
]


class QueueEntry(ModelSQL, ModelView):
    active = fields.Boolean('Active')
    triage_entry = fields.Many2One('gnuhealth.triage.entry', 'Triage Entry')
    appointment = fields.Many2One('gnuhealth.appointment', 'Appointment')
    encounter = fields.Many2One('gnuhealth.encounter', 'Encounter')
    busy = fields.Boolean('Busy', states={'readonly': True})
    encounter_components = fields.Function(fields.Char('Encounter Components'),
                                           'get_encounter_component_set')
                                           # searcher='search_component_set')
    encounter_component_count = fields.Function(
        fields.Integer('# Components'), 'get_encounter_component_set')
        # searcher='search_component_count')
    appointment_state = fields.Function(fields.Selection(APPOINTMENT_STATES,
                                        'State'), 'get_appointment_state')
                                        # searcher='search_appointment_state')

    # get_encounter_component_set = returns a csv string with the most
    # recent component listed first
    def get_encounter_component_set(self, name):
        if self.encounter:
            if name == 'encounter_component_count':
                return len(self.encounter.components)
            elif name == 'encounter_components':
                complist = [x.component_type for x in self.encounter.components]
                return ', '.join(reversed(complist))

        if name == 'encounter_component_count':
            return 0
        else:  # name == 'encounter_components':
            return ''

    # search_component_set : a domain that searches for queue items
    # with encounters that have component types entered

    # search_component_count: return a domain to search for queue entries
    # based on the number of components the associated encounter has

    # get_appointment_state: return one from APPOINTMENT_STATES based
    # on the state of the associated appointment and encounter
    def get_appointment_state(self, name):
        if name == 'appointment_state':
            if self.appointment:
                if self.appointment.state == 'arrived':
                    return '3'
                elif self.appointment.state == 'processing':
                    return '4'
                elif self.appointment.state in ['done', 'user_cancelled',
                                                'center_cancelled', 'no_show']:
                    return '5'
            elif self.triage_entry and self.triage_entry in ['tobeseen', 'resched', 'refer']:
                return '2'
        return '1'

    # search_appointment_state: domain that searches queueEntries based
    # the specified state entered.


