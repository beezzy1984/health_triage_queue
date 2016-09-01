
from datetime import datetime
from trytond.pool import Pool
from trytond.model import ModelView, ModelSQL, fields
from trytond.pyson import Eval, Not, Bool, Or, And
from .common import plus_none, SEX_OPTIONS

__all__ = ['PatientReferral']

REFERRAL_TYPES = [
    ('appt', 'Appointment'),
    ('admit', 'Admission'),
    ('consult', 'Consultation')
]
REFERRAL_SERVICE = [
    ('1', 'Emergency'),
    ('3', 'Urgent'),
    ('99', 'Routine')
]
RO_HERE = {'readonly': Or(~Eval('is_target', False),
                          Eval('signed_target', False)),
           'invisible': ~Eval('signed_local')}
RO_THERE = {'readonly': Eval('signed_local', False)}


class PatientReferral(ModelSQL, ModelView):
    'Referral'
    __name__ = 'gnuhealth.patient.referral'
    name = fields.Many2One('gnuhealth.patient', 'Patient', required=True,
                           states={'readonly': Or(Bool(Eval('from_triage')),
                                                  Eval('signed_local', False),
                                                  Bool(Eval('from_encounter')))})
    sex = fields.Function(fields.Selection(SEX_OPTIONS, 'Sex'),
                          'get_patient_data',
                          searcher='search_patient_data')
    sex_display = fields.Function(fields.Char('Sex'), 'get_patient_data')
    puid = fields.Function(fields.Char('UPI'), 'get_patient_data',
                           searcher='search_patient_data')
    age = fields.Function(fields.Char('Current Age'), 'get_patient_data')
    dob = fields.Function(fields.Date('Date of Birth'), 'get_patient_data',
                          searcher='search_patient_data')

    referral_date = fields.DateTime('Date/Time', required=True,
                                    states=RO_THERE)
    referred_by = fields.Many2One('gnuhealth.healthprofessional', 'Referred by',
                                  states=RO_THERE)
    reason = fields.Text('Reason for referral', states=RO_THERE)
    results = fields.Text('Consultant Notes/Findings', states=RO_HERE)
    from_institution = fields.Many2One('gnuhealth.institution', 'Referred From',
                                       required=True, states=RO_THERE)
    to_institution = fields.Many2One('gnuhealth.institution',
                                     'Refer To', required=True, states=RO_THERE)
    to_specialty = fields.Many2One('gnuhealth.specialty', 'Specialty',
                                   states=RO_THERE)
    referral_type = fields.Selection(plus_none(REFERRAL_TYPES), 'Type',
                                     sort=False, states=RO_THERE)
    service_requested = fields.Selection(plus_none(REFERRAL_SERVICE),
                                         'Treatment Required', sort=False,
                                         states=RO_THERE)
    from_triage = fields.Many2One('gnuhealth.triage.entry', 'Triage Entry',
                                  states=RO_THERE)
    from_encounter = fields.Many2One('gnuhealth.encounter', 'Encounter',
                                     states=RO_THERE)
    to_appointment = fields.Many2One('gnuhealth.appointment', 'Appointment',
                                     domain=[('institution', '=',
                                              Eval('to_institution'))],
                                     states=RO_HERE)
    is_local = fields.Function(fields.Boolean('Originated here'),
                               'get_is_local', searcher='search_target_local')
    is_target = fields.Function(fields.Boolean('Referred here'),
                                'get_is_target', searcher='search_target_local')
    referer = fields.Many2One('gnuhealth.healthprofessional', 'Signed By',
            states={'readonly': True,
                    'invisible': ~Bool(Eval('referer_sign_date'))})
    referer_sign_date = fields.DateTime('Sign date',
            states={'readonly': True,
                    'invisible': ~Bool(Eval('referer'))})
    signed_local = fields.Function(fields.Boolean('Referer Signed'),
                                   'get_signed', searcher='search_signed')
    referee = fields.Many2One('gnuhealth.healthprofessional', 'Referee',
            states={'readonly': True,
                    'invisible': ~Bool(Eval('referee_sign_date'))})
    referee_sign_date = fields.DateTime('Referee Sign Date',
            states={'readonly': True,
                    'invisible': ~Bool(Eval('referee'))})
    signed_target = fields.Function(fields.Boolean('Referee Signed'),
                                   'get_signed', searcher='search_signed')

    @classmethod
    def __setup__(cls):
        super(PatientReferral, cls).__setup__()
        cls._error_messages.update({
            'health_professional_warning': 'No health professional '
            'associated with this user'
        })
        cls._buttons.update({
            'btn_sign_local': {
                'invisible': Eval('signed_local', False),
                'readonly': ~Bool(Eval('name', False))
            },
            'btn_sign_target': {
                'invisible': Or(Eval('signed_target', False),
                                ~Eval('signed_local', False),
                                ~Eval('is_target', False))
            }
        })

    def get_patient_data(self, name):
        return getattr(self.name, name)

    @classmethod
    def search_patient_data(*arg, **kwarg):
        pass

    @staticmethod
    def default_referral_date():
        return datetime.now()

    @staticmethod
    def default_referred_by():
        HP = Pool().get('gnuhealth.healthprofessional')
        hp = HP.get_health_professional()
        return hp

    @staticmethod
    def default_from_institution():
        HI = Pool().get('gnuhealth.institution')
        hi = HI.get_institution()
        return hi

    @staticmethod
    def default_is_local():
        return True
        # always local when new

    @classmethod
    def get_is_local(cls, instances, name):
        HI = Pool().get('gnuhealth.institution')
        hi = HI.get_institution()
        local_list = [(i.id, int(i.from_institution) == hi)
                      for i in instances]
        return dict(local_list)

    @classmethod
    def get_is_target(cls, instances, name):
        HI = Pool().get('gnuhealth.institution')
        hi = HI.get_institution()
        target_list = [(i.id, int(i.to_institution) == hi)
                       for i in instances]
        return dict(target_list)

    @classmethod
    def search_target_local(cls, name, clause):
        fld, operator, operand = clause
        HI = Pool().get('gnuhealth.institution')
        hi = HI.get_institution()
        field_name = {'is_local': 'from_institution',
                      'is_target': 'to_institution'}[name]
        find_made_here = False
        if operand is True:
            if operator in ('=', 'in', 'is', '<=', '>=', 'like', 'ilike'):
                find_made_here = True
            else:
                find_made_here = False
        else:
            if operator in ('!=', 'not in', 'not like'):
                find_made_here = True
            else:
                find_made_here = False
        if find_made_here:
            return [(field_name, '=', hi)]
        else:
            return [(field_name, '!=', hi)]

    @classmethod
    def do_sign(cls, referrals, sign_local=True):
        HP = Pool().get('gnuhealth.healthprofessional')
        signing_hp = HP.get_health_professional()
        if not signing_hp:
            cls.raise_user_error('health_professional_warning')
        local_sign = []
        target_sign = []
        now = datetime.now()
        for referral in referrals:
            if sign_local:
                local_sign.append(referral)
            else:
                target_sign.append(referral)
        if local_sign:
            local_write = {'referer': signing_hp, 'referer_sign_date': now}
            cls.write(local_sign, local_write)
        if target_sign:
            target_write = {'referee': signing_hp, 'referee_sign_date': now}
            cls.write(target_sign, target_write)

    @classmethod
    @ModelView.button
    def btn_sign_local(cls, referrals):
        cls.do_sign(referrals, True)

    @classmethod
    @ModelView.button
    def btn_sign_target(cls, referrals):
        cls.do_sign(referrals, False)

    @classmethod
    def get_signed(cls, instances, name):
        if name == 'signed_local':
            field_name = 'referer_sign_date'
        else:
            field_name = 'referee_sign_date'
        outlist = [(int(i), getattr(i, field_name) is not None)
                   for i in instances]
        return dict(outlist)

    @classmethod
    def search_signed(cls, name, clause):
        fld, operator, operand = clause
        operdict = {'=': '!=', '!=': '='}
        if name == 'signed_local':
            field_name = 'referer_sign_date'
        else:
            field_name = 'referee_sign_date'
        if operator in operdict:
            if operand is True:
                return [(field_name, operdict[operator], None)]
            else:
                return [(field_name, operator, None)]

    @staticmethod
    def default_signed_local():
        return False

    @staticmethod
    def default_signed_target():
        return False


