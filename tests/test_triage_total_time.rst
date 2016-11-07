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



Get Triage Model::



    >>> Triage = Model.get('gnuhealth.triage.entry')

    >>> HealthProfessional = Model.get('gnuhealth.healthprofessional')

    >>> Notification = Model.get('gnuhealth.disease_notification')

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



Test Scenario::


    >>> triage.save()

    >>> triage.total_time == None
    False

    >>> COV.stop()

    >>> COV.save()

    >>> report = COV.html_report()
