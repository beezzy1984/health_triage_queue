
from trytond.pool import Pool
from trytond.model import ModelView, ModelSQL, fields
from trytond.pyson import Eval, Not, Equal, Or, Bool, In, Len

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

REQD_IF_NOPATIENT = {'required': Not(Bool(Eval('patient'))),
                     'readonly': Bool(Eval('patient'))}


class TriageEntry(ModelSQL, ModelView):
    'Triage Entry'
    __name__ = 'gnuhealth.triage.entry'
    firstname = fields.Char('First Name', states=REQD_IF_NOPATIENT)
    lastname = fields.Char('Last Name', states=REQD_IF_NOPATIENT)
    sex = fields.Selection(SEX_OPTIONS, 'Sex', states=REQD_IF_NOPATIENT)
    age = fields.Char('Age', states=REQD_IF_NOPATIENT)
    id_type = fields.Selection(ID_TYPES, 'ID Type', states={
        'required': Bool(Eval('id_number'))}, sort=False)
    id_number = fields.Char('ID Number')
    id_display = fields.Function(fields.Char('ID Display'), 'get_id_display')
    patient = fields.Many2One('gnuhealth.patient', 'Patient')
    priority = fields.Selection(TRIAGE_PRIO, 'Priority')
    injury = fields.Boolean('Injury')
    review = fields.Boolean('Review')
    status = fields.Selection(TRIAGE_STATUS, 'Status', sort=False)
    notes = fields.Text('Notes')
    upi = fields.Function(fields.Char('UPI'), 'get_patient_party_field')
    name = fields.Function(fields.Char('Name'), 'get_name',
                           searcher='search_name')
    patient_search = fields.Function(fields.One2Many(
                                     'gnuhealth.patient', None, 'Patients'),
                                     'patient_search_result')

    @staticmethod
    def default_priority():
        return '0'

    @staticmethod
    def default_status():
        return 'pending'

    @classmethod
    def get_name(cls, instances, name):
        if name == 'name':
            out = dict([(i.id, i.patient.name.name) for i in instances
                        if i.patient])
            out.update([(i.id, '%s, %s' % (i.lastname, i.firstname))
                        for i in instances if not i.patient])
        return out

    @classmethod
    def search_name(cls, name, clause):
        fld, operator, operand = clause
        return ['OR',
                ('patient.name.name', operator, operand),
                ('firstname', operator, operand),
                ('lastname', operator, operand)]

    @classmethod
    def get_patient_party_field(cls, instances, name):
        out = dict([(i.id, '') for i in instances])
        if name == 'name':
            out = dict([(i.id, i.patient.puid) for i in instances
                        if i.patient])
        return out

    def get_id_display(self, name):
        idtypedict = dict(ID_TYPES)
        if self.id_number and self.id_type:
            return ': '.join([idtypedict.get(self.id_type, '??'),
                              self.id_number])
        else:
            return ''


    def patient_search_result(self, name):
        # ToDo: perform search against patient/party and return
        # the ones that match.
        # the domain should include :
        # lastname, firstname, sex, id_type, id_number
        return []
