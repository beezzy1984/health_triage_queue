
def plus_none(option_list):
    '''adds a None option to the top of a selection listing'''
    return [(None, '')] + option_list


SEX_OPTIONS = [('m', 'Male'), ('f', 'Female'), ('u', 'Unknown')]

MENARCH = (8, 60)

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
APM = {None: 99, 'a': 5, 'b': 3, 'c': 1}

# Max value for triage priority
# based on the ESI = Emergency Severity Index
# 99 used as Not-Prioritised
TRIAGE_MAX_PRIO = 99

# ESI_NAMES = ['Normal', 'Urgent', 'Very Urgent', 'Emergency', 'Resuscitation']
ESI_NAMES = ['Non-Urgent', 'Less Urgent', 'Urgent', 'Very Urgent', 'Immediate']
ESI_MAX_PRIO = len(ESI_NAMES)

TRIAGE_PRIO = [('99', 'Not prioritised'), ('77', 'Medical Alert')] + [
    (str(x), '%d - %s' % (x, y)) for x, y in
    zip(range(ESI_MAX_PRIO, 0, -1), ESI_NAMES)]
