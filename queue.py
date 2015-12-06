
from trytond.pool import Pool
from trytond.model import ModelView, ModelSQL, fields
from trytond.pyson import Eval, Not, Equal, Or, Greater, In, Len
from .triage import TriageEntry, SEX_OPTIONS

QUEUE_ENTRY_STATES = [
    ('0', ''),
    ('1', 'Triage'),
    ('2', 'Registration'),
    ('3', 'Nurse/Pre-Evaluation'),
    ('4', 'Evaluation'),
    ('99', 'Done'),
]


class QueueEntry(ModelSQL, ModelView):
    'Queue Entry'
    __name__ = 'gnuhealth.patient.queue_entry'

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
    entry_state = fields.Function(fields.Selection(QUEUE_ENTRY_STATES, 'State'),
                                  'get_qentry_state',
                                  searcher='search_qentry_state')
    name = fields.Function(fields.Char('Name'), 'get_patient_name',
                           searcher='search_patient_name')
    upi_mrn_id = fields.Function(fields.Char('UPI/MRN/ID#'), 'get_upi_mrn_id',
                                 searcher='search_upi_mrn_id')
    sex = fields.Function(fields.Selection(SEX_OPTIONS, 'Sex'),
                          'get_sex', searcher='search_sex')
    age = fields.Function(fields.Char('Age'), 'get_age')  #, searcher='search_age')
    notes = fields.Function(fields.Text('Notes/Info'), 'get_notes_info')

    @classmethod
    def get_patient_name(cls, instances, name):
        out = dict([(x.id, x.appointment.patient.name.name) for x in instances
                    if x.appointment])
        out.update([(x.id, x.triage_entry.name) for x in instances
                    if x.triage_entry and not x.appointment])
        return out

    @classmethod
    def search_patient_name(cls, name, clause):
        fld, operator, operand = clause
        if name == 'name':
            dom = ['OR']
            for fld in ('triage_entry.name',
                        'appointment.patient.name.name'):
                dom.append((fld, operator, operand))
            return dom

    @classmethod
    def get_upi_mrn_id(cls, instances, name):
        out = dict([(x.id, 'UPI:%s  | MRN: %s' % (
                        x.appointment.patient.puid,
                        x.appointment.patient.medical_record_num))
                    for x in instances if x.appointment])

        out.update([(x.id, x.triage_entry.id_display)
                    for x in instances if x.triage_entry and not x.appointment])

    @classmethod
    def search_upi_mrn_id(cls, name, clause):
        fld, operator, operand = clause
        out = ['OR'] + [(f, operator, operand) for f in
                        ('triage_entry.id_number',
                         'appointment.patient.puid',
                         'triage_entry.patient.puid',
                         'triage_entry.patient.medical_record_num')]
        return out

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

    # get_qentry_state: return one from QUEUE_ENTRY_STATES based
    # on the state of the associated appointment and encounter
    def get_qentry_state(self, name):
        if name == 'appointment_state':
            if self.appointment:
                if self.appointment.state == 'arrived':
                    return '3'
                elif self.appointment.state == 'processing':
                    return '4'
                elif self.appointment.state in ['done', 'user_cancelled',
                                                'center_cancelled', 'no_show']:
                    return '99'
            elif self.triage_entry and self.triage_entry.status in [
                    'tobeseen', 'resched', 'refer']:
                return '2'
        return '1'

    # search_qentry_state: domain that searches queueEntries based
    # the specified state entered.
    @classmethod
    def search_qentry_state(cls, name, clause):
        field, operator, operand = clause
        if operator == '=':
            # the easy one and maybe the only one we'll need since
            # appointment_state is a selection field
            if operand == '1':
                return ['OR', ('triage_entry.status', '=', 'pending'),
                        ('appointment.state', '=', 'confirmed')]
            elif operand == '2':
                return [('triage_entry.status', 'in',
                         ['tobeseen', 'resched', 'refer'])]
            elif operand == '3':
                return [('appointment.state', '=', 'arrived')]
            elif operand == '4':
                return [('appointment.state', '=', 'processing')]
            else:
                return [('appointment.state', 'in', ['done', 'user_cancelled',
                                                     'center_cancelled',
                                                     'no_show'])]

    @classmethod
    def get_sex(cls, instances, name):
        out = dict([(x.id, x.appointment.patient.age)
                    for x in instances if x.appointment])
        out.update([(x.id, x.triage_entry.age)
                    for x in instances if not x.appointment])
        return out

    @classmethod
    def search_sex(cls, name, clause):
        fld, operator, operand = clause
        return ['OR', ('triage_entry.sex', operator, operand),
                ('appointment.patient.name.sex', operator, operand)]

    @classmethod
    def get_age(cls, instances, name):
        out = dict([(x.id, x.appointment.patient.age)
                    for x in instances if x.appointment])
        out.update([(x.id, x.triage_entry.age)
                    for x in instances if not x.appointment])
        return out

    # @classmethod
    # def search_age(cls, name, clause):
    #     pass

    def get_notes_info(self, name):
        if self.appointment:
            return self.appointment.comments
        else:
            return self.triage_entry.notes
