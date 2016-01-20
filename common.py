
SEX_OPTIONS = [('m', 'Male'), ('f', 'Female'), ('u', 'Unknown')]

ID_TYPES = [
    (None, ''),
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

# Appointment Priority Map
APM = {None: 5, 'a': 5, 'b': 3, 'c': 1}

# Max value for triage priority
# based on the ESI = Emergency Severity Index
TRIAGE_MAX_PRIO = 5

# ESI_NAMES = ['Normal', 'Urgent', 'Very Urgent', 'Emergency', 'Resuscitation']
ESI_NAMES = ['Non-Urgent', 'Less Urgent', 'Urgent', 'Emergent',
             'Resuscitation']

TRIAGE_PRIO = [(str(x), '%d - %s' % (x, y)) for x, y in
               zip(range(TRIAGE_MAX_PRIO, 0, -1), ESI_NAMES)]