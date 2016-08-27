
from datetime import datetime
from trytond.pool import Pool
from trytond.model import ModelView, ModelSQL, fields
from trytond.pyson import Eval, Not, Bool, Or
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
RO_HERE = {'readonly': Eval('is_local', True),
           'invisible': ~(Eval('id', 0) > 0)}
RO_THERE = {'readonly': ~Eval('is_local', True)}


class PatientReferral(ModelSQL, ModelView):
    'Referral'
    __name__ = 'gnuhealth.patient.referral'
    name = fields.Many2One('gnuhealth.patient', 'Patient', required=True,
                           states=RO_THERE)
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
    referer = fields.Many2One('gnuhealth.healthprofessional', 'Referred by',
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
                               'get_is_local')

    def get_patient_data(self, name):
        return getattr(self.name, name)

    @classmethod
    def search_patient_data(*arg, **kwarg):
        pass

    @staticmethod
    def default_referral_date():
        return datetime.now()

    @staticmethod
    def default_referer():
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
