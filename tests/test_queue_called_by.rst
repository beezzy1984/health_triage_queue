=====================================

Health Triage Scenario

=====================================


=====================================

General Setup

=====================================


Imports::

    >>> import coverage

    >>> from random import randrange

    >>> from datetime import datetime, timedelta

    >>> from dateutil.relativedelta import relativedelta

    >>> from decimal import Decimal

    >>> from proteus import config, Model, Wizard

    >>> from trytond.modules.health_disease_notification.tests.database_config import set_up_datebase

    >>> from trytond.modules.health_triage_queue.common import TRIAGE_PRIO, ID_TYPES

    >>> from trytond.modules.health_triage_queue.triage import TRIAGE_STATUS, URINALYSIS

    >>> from trytond.modules.health_jamaica.tryton_utils import (random_bool, random_id, code_gen, gen_age)



Create database::



    >>> COV = coverage.Coverage()

    >>> COV.start()

    >>> CONFIG = set_up_datebase()

    >>> CONFIG.pool.test = True



Get Models::



    >>> Triage = Model.get('gnuhealth.triage.entry')

    >>> HealthProfessional = Model.get('gnuhealth.healthprofessional')

    >>> Queue = Model.get('gnuhealth.patient.queue_entry')

    >>> Institution = Model.get('gnuhealth.institution')

    >>> institution, = Institution.find([('id', '=', random_id(89))])



Create Triage::



    >>> triage = Triage()


    >>> triage.firstname = code_gen()

    >>> triage.lastname = code_gen()

    >>> sexes = ['m', 'f', 'u']

    >>> sex = sexes[random_id(3)]

    >>> triage.sex = sex

    >>> triage.age = gen_age(random_id(89))

    >>> triage.id_type = ID_TYPES[random_id(12)][0]

    >>> triage.id_number = code_gen()

    >>> triage.priority = TRIAGE_PRIO[random_id(8) - 1][0]

    >>> triage.injury = random_bool()

    >>> triage.review = random_bool()

    >>> triage.status = TRIAGE_STATUS[0][0]

    >>> triage.complaint = 'Some random complaint'

    >>> triage.notes = 'Some random notes'

    >>> triage.systolic = randrange(60, 110, 10)

    >>> triage.diastolic = randrange(100, 150, 10)

    >>> triage.bpm = randrange(50, 80)

    >>> triage.respiratory_rate = randrange(60, 110, 10)

    >>> triage.osat = randrange(1, 10)

    >>> triage.temperature = randrange(20, 42)

    >>> if sex == 'f' or sex == 'u':
    ...     triage.pregnant = random_bool()
    ...     if triage.pregnant:
    ...         triage.lmp = datetime.now() + timedelta(days=random_id(100))
    ...     else:
    ...         triage.lmp = datetime.now() + timedelta(days=random_id(28))

    >>> triage.glucose = random_id(10)

    >>> triage.height = Decimal(randrange(60, 200))

    >>> triage.weight = Decimal(randrange(60, 200))

    >>> triage.uri_ph = Decimal(random_id(6))

    >>> triage.uri_specific_gravity = Decimal(random_id(10) - 1)

    >>> triage.uri_protein = URINALYSIS['default'][random_id(8) - 1][0]

    >>> triage.uri_blood = URINALYSIS['default'][random_id(8) - 1][0]

    >>> triage.uri_glucose = URINALYSIS['default'][random_id(8) - 1][0]

    >>> triage.uri_nitrite = URINALYSIS['nitrite'][random_id(7) - 1][0]

    >>> triage.uri_bilirubin = URINALYSIS['default'][random_id(8) - 1][0]

    >>> triage.uri_leuko = URINALYSIS['default'][random_id(8) - 1][0]

    >>> triage.uri_ketone = URINALYSIS['default'][random_id(8) - 1][0]

    >>> triage.uri_urobili = URINALYSIS['default'][random_id(8) - 1][0]

    >>> triage.malnutrition = random_bool()

    >>> dehydration = [None,'mild', 'moderate', 'severe']

    >>> triage.dehydration = dehydration[random_id(4) - 1]

    >>> triage.symp_fever = random_bool()

    >>> triage.symp_respiratory = random_bool()

    >>> triage.symp_jaundice = random_bool()

    >>> triage.symp_rash = random_bool()

    >>> triage.symp_hemorrhagic = random_bool()

    >>> triage.symp_neurological = random_bool()

    >>> triage.symp_arthritis = random_bool()

    >>> triage.symp_vomitting = random_bool()

    >>> triage.symp_diarrhoea = random_bool()

    >>> triage.institution = institution

    >>> triage.save()



Get Patient::



    >>> Patient = Model.get('gnuhealth.patient')


    >>> patient, = Patient.find([('id', '=', '1')])



Get Health Professional::



    >>> HealthProfessional = Model.get('gnuhealth.healthprofessional')

    >>> healthprof, = HealthProfessional.find([('id', '=', '1')])



Create Appointment::



    >>> Appointment = Model.get('gnuhealth.appointment')

    >>> appointment = Appointment()

    >>> appointment.patient = patient

    >>> appointment.type = 'ambulatory'

    >>> Specialty = Model.get('gnuhealth.specialty')

    >>> specialty, = Specialty.find([('code', '=', 'BIOCHEM')])

    >>> appointment.speciality = specialty

    >>> appointment.appointment_date = datetime.now()

    >>> appointment.save()

    >>> appointment.is_today
    True

    >>> appointment.tree_color
    'black'

    >>> appointment_next = Appointment()

    >>> appointment_next.patient = patient

    >>> appointment_next.type = 'ambulatory'

    >>> Specialty = Model.get('gnuhealth.specialty')

    >>> specialty, = Specialty.find([('code', '=', 'BIOCHEM')])

    >>> appointment_next.speciality = specialty

    >>> appointment_next.appointment_date = datetime.now() + timedelta(days=30)

    >>> appointment_next.save()

    >>> appointment_next.is_today
    False


Create Encounter::



    >>> appointment.state
    u'confirmed'

    >>> appointment.click('client_arrived')

    >>> appointment.tree_color
    'blue'

    >>> appointment_next.tree_color
    'black'

    >>> appointment.state
    u'arrived'

    >>> encounter_num = appointment.click('start_encounter')

    >>> Encounter = Model.get('gnuhealth.encounter')

    >>> encounter = Encounter()

    >>> encounter.appointment = appointment

    >>> encounter.patient = appointment.patient

    >>> encounter.start_time = datetime.now()

    >>> encounter.save()

    >>> appointment.tree_color
    'green'

    >>> encounter.primary_complaint = 'Fever, Headache, Muscle-ache'

    >>> Institution = Model.get('gnuhealth.institution')

    >>> institution, = Institution.find([('id', '=', '1')])

    >>> encounter.institution = institution

    >>> encounter.next_appointment = appointment_next

    >>> encounter.fvyt = random_bool()

    >>> Encounter_Ambulatory = Model.get('gnuhealth.encounter.ambulatory')

    >>> component_amb = Encounter_Ambulatory()

    >>> component_amb.systolic = 180

    >>> component_amb.diastolic = 88

    >>> component_amb.bpm = 80

    >>> component_amb.respiratory_rate = 35

    >>> component_amb.osat = 25

    >>> component_amb.temperature = 31

    >>> component_amb.childbearing_age = random_bool()

    >>> component_amb.pregnant = random_bool()

    >>> component_amb.lmp = datetime.now() + timedelta(days=-25)

    >>> component_amb.glucose = 5

    >>> component_amb.uri_ph = Decimal(3)

    >>> component_amb.uri_specific_gravity = Decimal(9)

    >>> component_amb.uri_protein = 'neg'

    >>> component_amb.uri_blood = '++'

    >>> component_amb.uri_glucose = '++++'

    >>> component_amb.uri_nitrite = 'trace'

    >>> component_amb.uri_bilirubin = '+++'

    >>> component_amb.uri_leuko = '++'

    >>> component_amb.uri_ketone = '+++'

    >>> component_amb.uri_urobili = '+'

    >>> component_amb.malnutrition = random_bool()

    >>> component_amb.dehydration = 'mild'

    >>> component_amb.encounter = encounter

    >>> component_amb.save()

    >>> Healthprof = Model.get('gnuhealth.healthprofessional')

    >>> healthprof, = Healthprof.find([('id', '=', '1')])

    >>> component_amb.signed_by = healthprof

    >>> component_amb.sign_time = datetime.now()

    >>> component_amb.save()

    >>> Encounter_Anth = Model.get('gnuhealth.encounter.anthropometry')

    >>> component_anth = Encounter_Anth()

    >>> component_anth.weight = Decimal(90)

    >>> component_anth.height = Decimal(170)

    >>> component_anth.head_circumference = Decimal(30)

    >>> component_anth.abdominal_circ = Decimal(35)

    >>> component_anth.hip = Decimal(50)

    >>> component_anth.whr = Decimal(1.5)

    >>> component_anth.signed_by = healthprof

    >>> component_anth.sign_time = datetime.now()

    >>> component_anth.encounter = encounter

    >>> component_anth.save()

    >>> Encounter_Mental_Stat = Model.get('gnuhealth.encounter.mental_status')

    >>> component_mental_stat = Encounter_Mental_Stat()

    >>> component_mental_stat.loc = 5

    >>> component_mental_stat.loc_eyes = '4'

    >>> component_mental_stat.loc_verbal = '2'

    >>> component_mental_stat.loc_motor = '6'

    >>> component_mental_stat.tremor = random_bool()

    >>> component_mental_stat.violent = random_bool()

    >>> component_mental_stat.mood = 'n'

    >>> component_mental_stat.orientation = random_bool()

    >>> component_mental_stat.memory = random_bool()

    >>> component_mental_stat.knowledge_current_events = random_bool()

    >>> component_mental_stat.judgement = random_bool()

    >>> component_mental_stat.abstraction = random_bool()

    >>> component_mental_stat.vocabulary = random_bool()

    >>> component_mental_stat.calculation_ability = random_bool()

    >>> component_mental_stat.object_recognition = random_bool()

    >>> component_mental_stat.praxis = random_bool()

    >>> component_mental_stat.signed_by = healthprof

    >>> component_mental_stat.sign_time = datetime.now()

    >>> component_mental_stat.encounter = encounter

    >>> component_mental_stat.save()

    >>> encounter.end_time = datetime.now() + timedelta(minutes=30)

    >>> encounter.save()

    >>> encounter.click('set_done')

    >>> encounter.click('sign_finish')

    >>> appointment.save()

    >>> appointment.save()

    >>> len(appointment.state_changes) == 3
    True

    >>> appointment.state_changes[0].target_state
    u'done'




Create Queue Entry::

    >>> queue_entry, = Queue.find([('triage_entry.id', '=', triage.id)])

    >>> queue_entry.active = True

    >>> queue_entry.encounter = encounter

    >>> queue_entry.busy = random_bool()

    >>> queue_entry.line_notes = "Just a few notes"

    >>> queue_entry.last_call = datetime.now() + timedelta(minutes=-random_id(80))

    >>> queue_entry.priority = random_id(5)

    >>> queue_entry.save()



Test Scenario::



    >>> queue_entry.called_by == None
    False

    >>> COV.stop()

    >>> COV.save()

    >>> report = COV.html_report()
