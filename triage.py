# -*- coding: utf-8 -*-

from datetime import datetime
from trytond.pool import Pool
from trytond.model import ModelView, ModelSQL, fields
from trytond.pyson import Eval, Not, Equal, Or, Bool, In, Len
from .common import (ID_TYPES, SEX_OPTIONS, TRIAGE_MAX_PRIO, TRIAGE_PRIO,
                     MENARCH)
from trytond.modules.health_jamaica.tryton_utils import get_model_field_perm
from trytond.modules.health_jamaica.tryton_utils import get_elapsed_time
from trytond.modules.health_jamaica.tryton_utils import localtime

TRIAGE_STATUS = [
    ('pending', 'Pending'),
    ('triage', 'Triage'),
    ('tobeseen', 'To be seen'),
    ('admit', 'Admit to Ward'),
    ('resched', 'Reschedule'),
    ('referin', 'Refer to another Department'),
    ('refer', 'Refer to Other Facility'),
    ('home', 'Treated and Sent Home'),
    ('incomplete', 'Triage Incomplete')
]
TRIAGE_STATUS_LOOKUP = dict(TRIAGE_STATUS)
MED_ALERT = TRIAGE_PRIO[1][0]
REQD_IF_NOPATIENT = {'required': Not(Bool(Eval('patient'))),
                     'invisible': Bool(Eval('patient')),
                     'readonly': Eval('done', False)}

URINALYSIS = {
    'default': [
        ('neg', 'negative'),
        ('trace', 'trace'),
        ('+', '+'), ('++', '2+'),
        ('+++', '3+'), ('++++', '4+'),
        ('+++++', '5+')],
    'nitrite': [
        ('neg.', 'negative'),
        ('trace', 'trace'),
        ('small', 'small'),
        ('moderate', 'moderate'),
        ('large', 'large'),
        ('large+', 'large+')]
}

STATE_NO_MENSES = {'readonly': Or(~Eval('childbearing_age', True),
                                  Eval('done', False)),
                   'invisible': ~Eval('childbearing_age', False)}

SIGNED_STATES = {'readonly': Eval('done', False)}


class TriageEntry(ModelSQL, ModelView):
    'Triage Entry'
    __name__ = 'gnuhealth.triage.entry'
    firstname = fields.Char('First Name', states=REQD_IF_NOPATIENT)
    lastname = fields.Char('Last Name', states=REQD_IF_NOPATIENT)
    sex = fields.Selection([(None, '')] + SEX_OPTIONS, 'Sex',
                           states=REQD_IF_NOPATIENT)
    age = fields.Char('Age', states=REQD_IF_NOPATIENT)
    sex_display = fields.Function(fields.Selection(SEX_OPTIONS, 'Sex'),
                                  'get_sex_age_display')
    age_display = fields.Function(fields.Char('Age'), 'get_sex_age_display')
    id_type = fields.Selection(ID_TYPES, 'ID Type', states={
        'required': Bool(Eval('id_number')),
        'readonly': Bool(Eval('patient'))},
        sort=False)
    id_number = fields.Char('ID Number',
            states={'readonly': Or(Bool(Eval('patient')), Eval('done', False))})
    id_display = fields.Function(fields.Char('UPI/MRN'), 'get_id_display',
                                 searcher='search_id')
    patient = fields.Many2One('gnuhealth.patient', 'Patient',
            states={'readonly': Or(~Eval('can_do_details', False),
                                   Eval('done', False))})
    priority = fields.Selection(TRIAGE_PRIO, 'ESI Priority', sort=False,
            help='Emergency Severity Index Triage Level',
            states={'invisible': ~(Eval('id', 0) > 0),
                    'readonly': Or(~Eval('can_do_details', False),
                                   Eval('done', False))})
    medical_alert = fields.Function(fields.Boolean('Medical Alert',
            states={'invisible': Or(Eval('can_do_details', False),
                                    ~In(Eval('status'), ['triage', 'pending']),
                                    ~In(Eval('priority'), ['99', '77']))}),
            'get_medical_alert', setter='set_medical_alert')
    injury = fields.Boolean('Injury', states=SIGNED_STATES)
    review = fields.Boolean('Review', states=SIGNED_STATES)
    status = fields.Selection(TRIAGE_STATUS, 'Status', sort=False,
            states={'readonly': Or(~Eval('can_do_details', False),
                                   Eval('done', False))})
    status_display = fields.Function(fields.Char('Status'),
                                     'get_status_display')
    complaint = fields.Char('Primary Complaint', states=SIGNED_STATES)
    notes = fields.Text('Notes (edit)', states=SIGNED_STATES)
    note_entries = fields.One2Many('gnuhealth.triage.note', 'triage_entry',
                                   'Note entries')
    note_display = fields.Function(fields.Text('Notes'), 'get_note_display')
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
        u'Temperature (°C)', digits=(4, 1),
        help='Temperature in degrees celsius', states=SIGNED_STATES)
        # domain=[('temperature', '>', 25), ('temperature', '<', 50)])
    childbearing_age = fields.Function(fields.Boolean('Childbearing Age'),
                                       'get_childbearing_age')
    pregnant = fields.Boolean('Pregnant', states=STATE_NO_MENSES)
    lmp = fields.Date('Last Menstrual Period', states=STATE_NO_MENSES,
                      help='Date last menstrual period started')
    glucose = fields.Float(
        'Glucose (mmol/l)', digits=(5, 1),
        help='mmol/l. Reading from glucose meter', states=SIGNED_STATES,
        domain=['OR', ('glucose', '=', None), ['AND', ('glucose', '>', 0),
                                               ('glucose', '<', 55.1)]])
    height = fields.Numeric('Height (cm)', digits=(4, 1), states=SIGNED_STATES)
    weight = fields.Numeric('Weight (kg)', digits=(3, 2), states=SIGNED_STATES)
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
    symp_fever = fields.Boolean('Fever', states=SIGNED_STATES)
    symp_respiratory = fields.Boolean('Respiratory', help="breathing problems",
                                      states=SIGNED_STATES)
    symp_jaundice = fields.Boolean('Jaundice', states=SIGNED_STATES)
    symp_rash = fields.Boolean('Rash', states=SIGNED_STATES)
    symp_hemorrhagic = fields.Boolean("Hemorrhagic", states=SIGNED_STATES)
    symp_neurological = fields.Boolean("Neurological", states=SIGNED_STATES)
    symp_arthritis = fields.Boolean("Arthralgia/Arthritis",
                                    states=SIGNED_STATES)
    symp_vomitting = fields.Boolean("Vomitting", states=SIGNED_STATES)
    symp_diarrhoea = fields.Boolean("Diarrhoea", states=SIGNED_STATES)
    recent_travel_contact = fields.Char(
        "Countries visited/Contact with traveller",
        states=SIGNED_STATES,
        help="Countries visited or from which there was contact with a "
             "traveller within the last six weeks")
    institution = fields.Many2One('gnuhealth.institution', 'Institution',
                                  states={'readonly': True})
    _history = True  # enable revision control from core
    can_do_details = fields.Function(fields.Boolean('Can do triage details'),
                                     'get_do_details_perm')
    first_contact_time = fields.Function(fields.Text('First Contact Time'),
                                         'get_first_time_contact')
    done = fields.Boolean('Done', states={'invisible': True})
    end_time = fields.DateTime('End Time', help='Date and time triage ended',
           states={'readonly': Or(~Eval('can_do_details', False),
                                  Eval('done', False))})
    post_appointment = fields.Many2One('gnuhealth.appointment', 'Appointment')
    # signed_by = fields.Many2One('gnuhealth.healthprofessional'', 'Signed By')
    # sign_time = fields.DateTime('Signed on')
    total_time = fields.Function(fields.Char('Triage Time',
        states={'invisible': ~Eval('done', False)}), 'get_triage_time')

    @classmethod
    def __setup__(cls):
        super(TriageEntry, cls).__setup__()
        cls._buttons.update({
            'set_done': {
                'readonly': ~Eval('can_do_details', False),
                'invisible': Or(In(Eval('status'), ['pending', 'triage']),
                                Eval('done', False))
            },
            'go_referral': {
                'readonly': ~Eval('can_do_details', False),
                'invisible': ~In(Eval('status'), ['refer', 'referin'])
            }
        })

    @classmethod
    def _swapnote(cls, vdict):
        '''swaps out the value in the notes field for an entry that creates
        a new gnuhealth.triage.note model instance'''
        new_note = vdict.get('notes', '')
        if new_note.strip():
            new_note = new_note.strip()
            noteobj = ('create', [{'note': new_note}])
            vdict.setdefault('note_entries', []).append(noteobj)
            vdict['notes'] = u''  # toDo: remove this for next release and use vdict.pop
        return vdict

    @classmethod
    def make_priority_updates(cls, triage_entries, values_to_write):
        if ('priority' in values_to_write and
                'queue_entry' not in values_to_write):
            prio = int(values_to_write['priority'])
            queue_model = Pool().get('gnuhealth.patient.queue_entry')
            qentries = queue_model.search(
                [('triage_entry', 'in', triage_entries)])
            values_to_write['queue_entry'] = [('write', map(int, qentries),
                                               {'priority': prio})]
        # force end-time to now if none entered and the prompt ignored
        if (values_to_write.get('done', False) and
                not values_to_write.get('end_time', False)):
            values_to_write['end_time'] = datetime.now()

        return triage_entries, cls._swapnote(values_to_write)

    @classmethod
    def create(cls, vlist):
        # add me to the queue when created
        for vdict in vlist:
            if not vdict.get('queue_entry'):
                if vdict.get('medical_alert') is True:
                    vqprio = MED_ALERT
                else:
                    try:
                        vqprio = int(vdict.get('priority', TRIAGE_MAX_PRIO))
                    except TypeError:
                        vqprio = int(TRIAGE_MAX_PRIO)

                vdict['queue_entry'] = [('create',
                                         [{'busy': False,
                                           'priority': vqprio}])]
                vdict = cls._swapnote(vdict)  # in case there's a note now
        return super(TriageEntry, cls).create(vlist)

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

    def get_triage_time(self, name):
        return get_elapsed_time(self.create_date, self.end_time) \
        if self.done else get_elapsed_time(self.create_date, datetime.now())

    def get_name(self, name):
        if name == 'name':
            if self.patient:
                return self.patient.name.name
            else:
                return '%s, %s' % (self.lastname, self.firstname)
        return ''

    @classmethod
    def search_name(cls, name, clause):
        fld, operator, operand = clause
        return ['OR',
                ('patient.name.name', operator, operand),
                ('firstname', operator, operand),
                ('lastname', operator, operand)]

    @classmethod
    def search_id(cls, name, clause):
        fld, operator, operand = clause
        return ['OR'
                ('patient.name.upi', operator, operand),
                ('patient.medical_record_num', operator, operand),
                ('id_number', operator, operand)]

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
            return '{} / {}'.format(self.patient.puid,
                                    self.patient.medical_record_num)
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

    def get_status_display(self, name):
        return TRIAGE_STATUS_LOOKUP.get(self.status)

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
                age = 7  # hack to make a default false for BHC
            if age < MENARCH[0] or age > MENARCH[1]:
                return False
        return True

    def get_sex_age_display(self, name):
        field = name[:3]
        if self.patient:
            return getattr(self.patient, field)
        else:
            return getattr(self, field)


    @fields.depends('sex', 'patient')
    def on_change_with_childbearing_age(self, *a, **k):
        if self.patient:
            return self.patient.childbearing_age
        else:
            if self.sex == 'm':
                return False
            else:
                return True

    @classmethod
    def get_medical_alert(cls, instances, name):
        out = [(i.id, i.priority == MED_ALERT) for i in instances]
        return dict(out)

    @classmethod
    def set_medical_alert(cls, instances, name, value):
        to_write = []
        if value is False:
            return
        for i in instances:
            if i.priority > MED_ALERT:
                to_write.append(i)
        cls.write(to_write, {'priority': MED_ALERT})

    @classmethod
    def get_do_details_perm(cls, instances, name):
        user_has_perm = get_model_field_perm(cls.__name__, name, 'create',
                                             default_deny=False)
        outval = dict([(x.id, user_has_perm) for x in instances])
        return outval

    @staticmethod
    def default_can_do_details():
        user_has_perm = get_model_field_perm('gnuhealth.triage.entry',
                                             'can_do_details', 'create',
                                             default_deny=False)
        return user_has_perm

    @staticmethod
    def default_childbearing_age():
        return True

    @staticmethod
    def uri_selection():
        return [(None, '')] + URINALYSIS['default']

    @staticmethod
    def uri_nitrite_selection():
        return [(None, '')] + URINALYSIS['nitrite']

    def get_first_time_contact(self, name):
        '''This method gets the date and time 
           this person was first made contact
           with by the attending staff'''
        return localtime(self.create_date).strftime('%F %T')

    @staticmethod
    def default_institution():
        HI = Pool().get('gnuhealth.institution')
        return HI.get_institution()

    def get_note_display(self, name):
        notes = []
        if self.note_entries:
            return u'\n---\n'.join(
                map(lambda x: u' :\n'.join([x.byline, x.note]),
                    self.note_entries))
        else:
            return ''


    @classmethod
    @ModelView.button_action('health_triage_queue.act_triage_referral_starter')
    def go_referral(cls, queue_entries):
        pass

    @classmethod
    @ModelView.button
    def set_done(cls, entries):
        '''set done=True on the triage entry'''
        save_data = {'done': True}
        for entry in entries:
            if not entry.end_time:
                cls.raise_user_warning(
                    'triage_end_date_warn1',
                    'End time has not been set.\nThe current Date and time '
                    'will be used.')
                save_data.update(end_time=datetime.now())
        cls.write(entries, save_data)


class TriageNote(ModelView, ModelSQL):
    'Triage Entry Note'
    __name__ = 'gnuhealth.triage.note'
    triage_entry = fields.Many2One('gnuhealth.triage.entry',
                                  'Queue Entry', required=True)
    note = fields.Text('Note', required=True)
    created = fields.Function(fields.DateTime('Created at'), 'get_writeinfo')
    creator = fields.Function(fields.Char('Creator'), 'get_writeinfo')
    byline = fields.Function(fields.Char('By Line'), 'get_writeinfo')

    @classmethod
    def __setup__(cls):
        super(TriageNote, cls).__setup__()
        cls._order = [('write_date', 'DESC'), ('create_date', 'DESC')]

    @classmethod
    def get_writeinfo(cls, instances, name):
        if name == 'created':
            conv = lambda x: (x.id,
                              x.write_date and x.write_date or x.create_date)
        elif name == 'creator':
            conv = lambda x: (x.id, x.write_uid.name if x.write_uid
                              else x.create_uid.name)
        elif name == 'byline':
            conv = lambda x: (x.id, u'%s, %s' % (
                              localtime(x.create_date
                                        ).strftime('%Y-%m-%d %H:%M'),
                              x.create_uid.name))
        else:
            conv = lambda x: (x.id, None)
        return dict(map(conv, instances))

