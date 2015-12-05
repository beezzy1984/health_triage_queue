
from trytond.pool import Pool
from trytond.model import ModelView, ModelSQL, fields
from trytond.pyson import Eval, Not, Equal, Or, Greater, In, Len

SEX_OPTIONS = [('m', 'Male'), ('f', 'Female'), ('u', 'Unknown')]
ID_TYPES = [
    ('trn', 'TRN'),
    ('medical_record', 'Medical Record'),
    ('upi', 'ePAS UPI'),
    ('pathID ', 'PATH ID'),
    ('gojhcard', 'GOJ Health Card'),
    ('votersid', 'GOJ Voter\'s ID'),
    ('birthreg', 'Birth Registration ID'),
    ('ninnum', 'NIN #'),
    ('passport', 'Passport'),
    ('jm_license', 'Drivers License (JM)'),
    ('nonjm_license', 'Drivers License (non-JM)'),
    ('other', 'Other')]

TRIAGE_MAX_PRIO = 4
TRIAGE_PRIO = [(str(x), str(x)) for x in range(TRIAGE_MAX_PRIO+1)]
TRIAGE_STATUS = [
    ('pending', 'Pending'),
    ('tobeseen', 'To be seen'),
    ('resched', 'Reschedule'),
    ('refer', 'Refer to Other Facility'),
    ('done', 'Done')
]


class TriageEntry(ModelSQL, ModelView):
    'Triage Entry'
    __name__ = 'gnuhealth.triage.entry'
    firstname = fields.Char('First Name')
    lastname = fields.Char('Last Name')
    sex = fields.Selection(SEX_OPTIONS, 'Sex')
    age = fields.Char('Age')
    id_type = fields.Selection(ID_TYPES, 'ID Type')
    id_number = fields.Char('ID Number')
    patient = fields.Many2One('gnuheath.patient', 'Patient')
    priority = fields.Selection(TRIAGE_PRIO, 'Priority')
    injury = fields.Boolean('Injury')
    review = fields.Boolean('Review')
    status = fields.Selection(TRIAGE_STATUS, 'Status')
    notes = fields.Text('Notes')
    upi = fields.Function(fields.Char('UPI'), 'get_patient_party_field')
    name = fields.Function(fields.Char('Name'), 'get_name')
    patient_search = fields.Function(fields.One2Many(
                                     'gnuhealth.patient', None, 'Patients'),
                                     'patient_search_result')

    @classmethod
    def get_name(cls, instances, name):
        if name == 'name':
            out = dict([(i.id, i.patient.name.name) for i in instances
                        if i.patient])
            out.update([(i.id, '%s, %s' % (i.lastname, i.firstname))
                        for i in instances if not i.patient])
        return out

    @classmethod
    def get_patient_party_field(cls, instances, name):
        if name == 'name':
            out = dict([(i.id, i.patient.puid) for i in instances
                        if i.patient])
            out.update([(i.id, '') for i in instances if not i.patient])
        return out

    def patient_search_result(self, name):
        # ToDo: perform search against patient/party and return
        # the ones that match.
        # the domain should include :
        # lastname, firstname, sex, id_type, id_number
        return []
