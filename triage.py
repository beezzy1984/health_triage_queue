# -*- coding: utf-8 -*-

from trytond.pool import Pool
from trytond.model import ModelView, ModelSQL, fields
from trytond.pyson import Eval, Not, Equal, Or, Bool, In, Len
from .common import (ID_TYPES, SEX_OPTIONS, TRIAGE_MAX_PRIO, TRIAGE_PRIO,
                     MENARCH)

TRIAGE_STATUS = [
    ('pending', 'Pending'),
    ('tobeseen', 'To be seen'),
    ('resched', 'Reschedule'),
    ('refer', 'Refer to Other Facility'),
    ('done', 'Done')
]

REQD_IF_NOPATIENT = {'required': Not(Bool(Eval('patient'))),
                     'invisible': Bool(Eval('patient'))}

URINALYSIS = {
    'default': [
        ('neg', 'negative'),
        ('trace', 'trace'),
        ('+', '+'), ('++', '++'),
        ('+++', '+++'), ('++++', '++++')],
    'nitrite': [
        ('neg.', 'negative'),
        ('trace', 'trace'),
        ('small', 'small'),
        ('moderate', 'moderate'),
        ('large', 'large'),
        ('large+', 'large+')]
}

STATE_NO_MENSES = {'readonly': Not(Eval('childbearing_age', True)),
                   'invisible': Not(Eval('childbearing_age', True))}

SIGNED_STATES = {}


class TriageEntry(ModelSQL, ModelView):
    'Triage Entry'
    __name__ = 'gnuhealth.triage.entry'
    firstname = fields.Char('First Name', states=REQD_IF_NOPATIENT)
    lastname = fields.Char('Last Name', states=REQD_IF_NOPATIENT)
    sex = fields.Selection([(None, '')] + SEX_OPTIONS, 'Sex',
                           states=REQD_IF_NOPATIENT)
    age = fields.Char('Age', states=REQD_IF_NOPATIENT)
    id_type = fields.Selection(ID_TYPES, 'ID Type', states={
        'required': Bool(Eval('id_number')),
        'readonly': Bool(Eval('patient'))},
        sort=False)
    id_number = fields.Char('ID Number',
                            states={'readonly': Bool(Eval('patient'))})
    id_display = fields.Function(fields.Char('ID Display'), 'get_id_display')
    patient = fields.Many2One('gnuhealth.patient', 'Patient')
    priority = fields.Selection(TRIAGE_PRIO, 'ESI Priority', sort=False,
                                help='Emergency Severity Index Triage Level')
    injury = fields.Boolean('Injury')
    review = fields.Boolean('Review')
    status = fields.Selection(TRIAGE_STATUS, 'Status', sort=False)
    complaint = fields.Char('Primary Complaint')
    notes = fields.Text('Notes')
    upi = fields.Function(fields.Char('UPI'), 'get_patient_party_field')
    name = fields.Function(fields.Char('Name'), 'get_name',
                           searcher='search_name')
    patient_search = fields.Function(fields.One2Many(
                                     'gnuhealth.patient', None, 'Patients'),
                                     'patient_search_result')
    queue_entry = fields.One2Many('gnuhealth.patient.queue_entry',
                                  'triage_entry', 'Queue Entry', size=1)
    encounter = fields.Many2One('gnuhealth.encounter', 'Encounter')
    # Vital Signs
    systolic = fields.Integer('Systolic Pressure', states=SIGNED_STATES)
    diastolic = fields.Integer('Diastolic Pressure', states=SIGNED_STATES)
    bpm = fields.Integer(
        'Heart Rate (bpm)',
        help='Heart rate expressed in beats per minute', states=SIGNED_STATES)
    respiratory_rate = fields.Integer(
        'Respiratory Rate',
        help='Respiratory rate expressed in breaths per minute',
        states=SIGNED_STATES)
    osat = fields.Integer(
        'Oxygen Saturation',
        help='Oxygen Saturation(arterial).', states=SIGNED_STATES)
    temperature = fields.Float(
        u'Temperature (°C)', digits=(4, 2),
        help='Temperature in degrees celsius', states=SIGNED_STATES)
        # domain=[('temperature', '>', 25), ('temperature', '<', 50)])
    childbearing_age = fields.Function(fields.Boolean('Childbearing Age'),
                                       'get_childbearing_age')
    pregnant = fields.Boolean('Pregnant', states=STATE_NO_MENSES)
    lmp = fields.Date('Last Menstrual Period', states=STATE_NO_MENSES,
                      help='Date last menstrual period started')
    glucose = fields.Float(
        'Glucose (mmol/l)', digits=(5, 2),
        help='mmol/l. Reading from glucose meter', states=SIGNED_STATES)
    uri_ph = fields.Numeric('pH', digits=(1, 1), states=SIGNED_STATES)
    uri_specific_gravity = fields.Numeric('Specific Gravity',
                                          digits=(1, 3), states=SIGNED_STATES)
    uri_protein = fields.Selection(
        'uri_selection', 'Protein', sort=False, states=SIGNED_STATES)
    uri_blood = fields.Selection(
        'uri_selection', 'Blood', sort=False, states=SIGNED_STATES)
    uri_glucose = fields.Selection(
        'uri_selection', 'Glucose', sort=False, states=SIGNED_STATES)
    uri_nitrite = fields.Selection(
        'uri_nitrite_selection', 'Nitrite', sort=False, states=SIGNED_STATES)
    uri_bilirubin = fields.Selection(
        'uri_selection', 'Bilirubin', sort=False, states=SIGNED_STATES)
    uri_leuko = fields.Selection(
        'uri_selection', 'Leukocytes', sort=False, states=SIGNED_STATES)
    uri_ketone = fields.Selection(
        'uri_selection', 'Ketone', sort=False, states=SIGNED_STATES)
    uri_urobili = fields.Selection(
        'uri_selection', 'Urobilinogen', sort=False, states=SIGNED_STATES)

    malnutrition = fields.Boolean(
        'Malnourished',
        help='Check this box if the patient show signs of malnutrition.',
        states=SIGNED_STATES)

    dehydration = fields.Selection(
        [(None, 'No'), ('mild', 'Mild'), ('moderate', 'Moderate'),
         ('severe', 'Severe')],
        'Dehydration', sort=False,
        help='If the patient show signs of dehydration.',
        states=SIGNED_STATES)

    @classmethod
    def create(cls, vlist):
        # add me to the queue when created
        for vdict in vlist:
            if not vdict.get('queue_entry'):
                try:
                    vqprio = int(vdict.get('priority', TRIAGE_MAX_PRIO))
                except TypeError:
                    vqprio = int(TRIAGE_MAX_PRIO)

                vdict['queue_entry'] = [('create',
                                         [{'busy': False,
                                           'priority': vqprio}])]
        return super(TriageEntry, cls).create(vlist)

    @classmethod
    def make_priority_updates(cls, triage_entries, values_to_write):
        if ('priority' in values_to_write and
                'queue_entry' not in values_to_write):
            prio = int(values_to_write['priority'])
            queue_model = Pool().get('gnuhealth.patient.queue_entry')
            qentries = queue_model.search(
                ['AND', ('triage_entry', 'in', triage_entries),
                 ('appointment', '=', None)])  # , ('priority', '>', prio)]])
            values_to_write['queue_entry'] = [('write', map(int, qentries),
                                               {'priority': prio})]
        return triage_entries, values_to_write

    @classmethod
    def write(cls, records, values, *args):
        # update queue priority when mine updated
        # but only if it's higher or there's no appointment
        records, values = cls.make_priority_updates(records, values)
        newargs = []
        if args:
            arglist = iter(args)
            for r, v in zip(arglist, arglist):
                r, v = cls.make_priority_updates(r, v)
                newargs.extend([r, v])
        return super(TriageEntry, cls).write(records, values, *newargs)

    @staticmethod
    def default_priority():
        return str(TRIAGE_MAX_PRIO)

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
        if name == 'upi':
            out.update([(i.id, i.patient.puid) for i in instances
                        if i.patient])
        return out

    def get_id_display(self, name):
        idtypedict = dict(ID_TYPES)
        if self.patient:
            return self.patient.puid
        elif self.id_number and self.id_type:
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

    def get_childbearing_age(self, name):
        if self.patient:
            return self.patient.childbearing_age
        elif self.sex == 'm':
            return False
        else:
            age = self.age
            if age.isdigit():
                age = int(age)
            elif age[:-1].isdigit():
                age = int(age[:-1])
            else:
                age = 10
            if age < MENARCH[0] or age > MENARCH[1]:
                return False
        return True

    @fields.depends('sex', 'patient')
    def on_change_with_childbearing_age(self, *a, **k):
        if self.patient:
            return self.patient.childbearing_age
        else:
            if self.sex == 'm':
                return False
            else:
                return True

    @staticmethod
    def default_childbearing_age():
        return True

    @staticmethod
    def uri_selection():
        return [(None, '')] + URINALYSIS['default']

    @staticmethod
    def uri_nitrite_selection():
        return [(None, '')] + URINALYSIS['nitrite']
