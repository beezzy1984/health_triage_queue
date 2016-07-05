
from datetime import datetime
from trytond.pool import Pool
from trytond.model import ModelView, ModelSQL, fields
from trytond.pyson import Eval, Not, Equal, Or, Greater, In, Len, And
from .common import APM, SEX_OPTIONS, TRIAGE_MAX_PRIO

QUEUE_ENTRY_STATES = [
    ('0', ''),
    ('1', 'Triage'),
    ('2', 'Registration'),
    ('3', 'Pre-Evaluation/Nurse'),
    ('4', 'Evaluation'),
    ('99', 'Done')]

APPT_DONE_STATES = ['done', 'user_cancelled', 'center_cancelled', 'no_show']


class QueueEntry(ModelSQL, ModelView):
    'Queue Entry'
    __name__ = 'gnuhealth.patient.queue_entry'

    active = fields.Boolean('Active')
    triage_entry = fields.Many2One('gnuhealth.triage.entry', 'Triage Entry',
                                   states={'readonly': Eval('id', 0) > 0,
                                           'required': ~Eval('appointment')},
                                   select=True)
    appointment = fields.Many2One(
        'gnuhealth.appointment', 'Appointment', select=True,
        states={'readonly': Eval('id', 0) > 0,
                'required': ~Eval('triage_entry')})
    encounter = fields.Many2One('gnuhealth.encounter', 'Encounter',
                                states={'invisible': True})
    busy = fields.Boolean('Busy', states={'readonly': True}, select=True)
    line_notes = fields.Text('Line notes',
                             help="Quick note about this line/patient")
    encounter_components = fields.Function(
        fields.Char('Encounter Components'), 'get_encounter_component_set')
    encounter_component_count = fields.Function(
        fields.Integer('Component Count'), 'get_encounter_component_set')
    entry_state = fields.Function(fields.Selection(QUEUE_ENTRY_STATES,
                                  'State'), 'get_qentry_state',
                                  searcher='search_qentry_state')
    name = fields.Function(fields.Char('Name'), 'get_patient_name',
                           searcher='search_patient_name')
    upi_mrn_id = fields.Function(fields.Char('UPI/MRN/ID#'), 'get_upi_mrn_id',
                                 searcher='search_upi_mrn_id')
    sex = fields.Function(fields.Selection(SEX_OPTIONS, 'Sex'),
                          'get_sex', searcher='search_sex')
    age = fields.Function(fields.Char('Age'), 'get_age')
    primary_complaint = fields.Function(fields.Char('Primary Complaint'),
                                        'get_primary_complaint',
                                        searcher='search_primary_complaint')
    notes = fields.Function(fields.Text('Notes/Info'), 'get_notes_info')
    queue_notes = fields.One2Many('gnuhealth.patient.queue_entry_note',
                                  'queue_entry', 'Queue Notes',
                                  states={'invisible': True})
    last_call = fields.DateTime('Last Called', select=True)
    priority = fields.Integer('Priority', states={'readonly': True})
    last_touch = fields.Function(fields.DateTime('Last Seen', format='%H:%M'),
                                 'get_last_touch')
    last_toucher = fields.Function(fields.Char('Modification User'),
                                   'get_last_touch')
    specialty = fields.Function(fields.Many2One('gnuhealth.specialty',
                                                'Specialty'),
                                'get_specialty', searcher='search_specialty')
    visit_reason = fields.Function(fields.Char('Reason for Visit'),
                                   'get_visit_reason')

    @staticmethod
    def default_busy():
        return False

    @staticmethod
    def default_active():
        return True

    @staticmethod
    def default_priority():
        return TRIAGE_MAX_PRIO

    @classmethod
    def __setup__(cls):
        super(QueueEntry, cls).__setup__()
        cls.write_date.string = 'Last Modified'
        cls._order = [('priority', 'ASC'), ('last_call', 'ASC'),
                      ('create_date', 'ASC')]
        cls._buttons.update(
            btn_inspect={},
            btn_call={'readonly': Or(Eval('busy', False),
                                     Equal('99', Eval('entry_state', '0')))},
            btn_dismiss={'readonly': Not(Eval('busy', False))},
            btn_setup_appointment={
                'invisible': Not(Equal('2', Eval('entry_state', '0')))
            })
        cls._sql_constraints += [
            ('triage_uniq', 'UNIQUE(triage_entry)',
             'Triage entry already in the queue'),
            ('appointment_uniq', 'UNIQUE(appointment)',
             'Appointment already in the queue')]

    @classmethod
    def _swapout(cls, vdict, is_write=True):
        if vdict.get('line_notes', False):
            note = ('create', [{'note': vdict.pop('line_notes')}])
            # if is_write:
            #     note = ('create', [note])
            vdict.setdefault('queue_notes', []).append(note)
        if vdict.get('busy', False):
            vdict['last_call'] = datetime.now()
        return vdict

    @classmethod
    def write(cls, instances, values, *args):
        # overload to handle the following situation:
        # if something is written in line-notes, create a QueueEntryNote
        # object with that as the note. To do that we will
        values = cls._swapout(values)
        if args:
            newargs = [(x, cls._swapout(y)) for x, y in args]
        else:
            newargs = []
        return super(QueueEntry, cls).write(instances, values, *newargs)

    @classmethod
    def create(cls, vlist):
        # overload to create a QueueEntryNote if a line_note is included
        newvlist = [cls._swapout(v, False) for v in vlist]
        return super(QueueEntry, cls).create(newvlist)

    def get_patient_name(self, name):
        if self.appointment:
            return self.appointment.patient.rec_name
        elif self.triage_entry:
            return self.triage_entry.name
        else:
            return '[No Name]'

    def get_last_touch(self, name):
        if name == 'last_touch':
            return self.write_date and self.write_date or self.create_date
        elif name == 'last_toucher':
            return self.write_uid.name if self.write_uid else None
        return ''

    @classmethod
    def search_patient_name(cls, name, clause):
        fld, operator, operand = clause
        if name == 'name':
            dom = ['OR']
            for fld in ('triage_entry.name',
                        'appointment.patient.name.name'):
                dom.append((fld, operator, operand))
            return dom

    def get_upi_mrn_id(self, name):
        if self.appointment:
            return '%s; %s' % (self.appointment.patient.puid,
                               self.appointment.patient.medical_record_num)
        elif self.triage_entry:
            return self.triage_entry.id_display
        return ''

    @classmethod
    def search_upi_mrn_id(cls, name, clause):
        fld, operator, operand = clause
        out = ['OR'] + [(f, operator, operand) for f in
                        ('triage_entry.id_number',
                         'appointment.patient.puid',
                         'triage_entry.patient.puid',
                         'triage_entry.patient.medical_record_num')]
        return out

    # get_encounter_component_set = returns a csv string with the most
    # recent component listed first
    def get_encounter_component_set(self, name):
        if self.encounter:
            if name == 'encounter_component_count':
                return len(self.encounter.components)
            elif name == 'encounter_components':
                complist = [x.component_type
                            for x in self.encounter.components]
                return ', '.join(reversed(complist))

        if name == 'encounter_component_count':
            return 0
        else:  # name == 'encounter_components':
            return ''

    # search_component_set : a domain that searches for queue items
    # with encounters that have component types entered

    # search_component_count: return a domain to search for queue entries
    # based on the number of components the associated encounter has

    # get_qentry_state: return one from QUEUE_ENTRY_STATES based
    # on the state of the associated appointment and encounter
    def get_qentry_state(self, name):
        if self.appointment:
            if self.appointment.state == 'arrived':
                return '3'
            elif self.appointment.state == 'processing':
                return '4'
            elif self.appointment.state in ['done', 'user_cancelled',
                                            'center_cancelled', 'no_show']:
                return '99'
        elif self.triage_entry and self.triage_entry.status in [
                'tobeseen', 'resched', 'refer']:
            return '2'
        return '1'

    # search_qentry_state: domain that searches queueEntries based
    # the specified state entered.
    @classmethod
    def search_qentry_state(cls, name, clause):
        field, operator, operand = clause
        if operator == '=':
            # the easy one and maybe the only one we'll need since
            # entry_state is a selection field
            if operand == '1':
                return ['OR', ('triage_entry.status', '=', 'pending'),
                        ('appointment.state', '=', 'confirmed')]
            elif operand == '2':
                return [('triage_entry.status', 'in',
                         ['tobeseen', 'resched', 'refer'])]
            elif operand == '3':
                return [('appointment.state', '=', 'arrived')]
            elif operand == '4':
                return [('appointment.state', '=', 'processing')]
            else:
                return [('appointment.state', 'in', APPT_DONE_STATES)]
        elif operator == '!=':
            if operand == '99':
                # i.e. those that are not done
                return ['OR', ('appointment', '=', None),
                        ('appointment.state', 'not in', APPT_DONE_STATES)]
            if operand == '1':
                return ['OR',
                        ('triage_entry.status', 'in', ['tobeseen', 'resched',
                                                       'refer']),
                        ('appointment.state', 'in', ['arrived', 'processing'])]

    def get_sex(self, name):
        if self.appointment and self.appointment.patient:
            return self.appointment.patient.name.sex
        elif self.triage_entry:
            return self.triage_entry.sex
        else:
            return '--'

    @classmethod
    def search_sex(cls, name, clause):
        fld, operator, operand = clause
        return ['OR', ('triage_entry.sex', operator, operand),
                ('appointment.patient.name.sex', operator, operand)]

    def get_age(self, name):
        if self.appointment:
            return self.appointment.patient.age
        else:
            try:
                return self.triage_entry.age
            except AttributeError:
                return '--'

    # @classmethod
    # def search_age(cls, name, clause):
    #     pass

    def get_notes_info(self, name):
        details = []
        qnotes = []
        if self.queue_notes:
            qnotes = map(lambda x: u' - '.join([x.note, x.byline]),
                         self.queue_notes)
            details.extend([qnotes.pop(0), '-' * 20])
        if self.encounter:
            details.extend(['Encounter started: %s' % (
                       self.encounter.start_time.strftime('%c'),),
                       '    %s' % self.encounter.short_summary])
        elif self.appointment:
            a = self.appointment
            details.extend(
                [u' '.join(x) for x in [
                    (u'Appointment: ', a.appointment_date.strftime('%c')),
                    (u'    Specialty: ', a.speciality.name),
                    (u'    Status: ', a.state)]])
            # details.append('')
        # else:
        if self.triage_entry:
            details.append('Triage: Started %s,\n    status: %s' % (
                           self.triage_entry.create_date.strftime('%c'),
                           self.triage_entry.status_display))
            details.extend(['    %s' % x for x in
                            filter(None, [self.triage_entry.complaint,
                                          self.triage_entry.notes])])
        if qnotes:
            details.extend(['-' * 20] + qnotes)
        return u'\n'.join(details)

    @classmethod
    def get_primary_complaint(cls, instances, name):
        outd = {}
        for i in instances:
            ix = i.id
            outd[ix] = ''
            if i.encounter:
                outd[ix] = i.encounter.primary_complaint
            if i.triage_entry and not outd[ix]:
                outd[ix] = i.triage_entry.complaint
        return outd

    @classmethod
    def search_primary_complaint(cls, name, clause):
        subclause = tuple(clause[1:])
        tclause = ('triage_entry.complaint', ) + subclause
        eclause = ('encounter.primary_complaint', ) + subclause
        return ['OR', tclause, eclause]

    def get_specialty(self, name):
        if self.appointment:
            return self.appointment.speciality.id
        else:
            # return '[Triage]'
            return None

    @classmethod
    def search_specialty(cls, name, clause):
        subclause = tuple(clause[1:])
        newclause = ('appointment.speciality', ) + subclause
        return ['AND', ('appointment', '!=', None), newclause]

    # Button Functions for :
    # Inspect: Does the same as call except doesn't create new records nor
    #          does it update the busy flag on the queue entry
    # Call: sets busy=True for the selected queue item and opens the
    #        Triage, Appointment or Encounter object associated
    #        If the required related Appointment or Encounter no exist
    #        create it.
    # Dismiss: Sets busy=False for the selected queue item.

    @classmethod
    @ModelView.button_action('health_triage_queue.act_queue_inspect_starter')
    def btn_inspect(cls, queue_entries):
        pass

    @classmethod
    @ModelView.button_action('health_triage_queue.act_queue_call_starter')
    def btn_call(cls, queue_entries):
        # cls.write(queue_entries, {'busy': True})
        # we want to set this to True, but do we want to do it here
        # or should we do it after the thing launched has been saved or
        # somehow touched?
        pass

    @classmethod
    @ModelView.button_action('health_triage_queue.act_queue_dismiss_starter')
    def btn_dismiss(cls, queue_entries):
        pass

    @classmethod
    @ModelView.button_action('health_triage_queue.wiz_queue_appointment_setup')
    def btn_setup_appointment(cls, queue_entries):
        pass

    @classmethod
    def appointment_arrive_trigger(cls, appointments, trigger):
        # create a queue entry item for each appointment with state=arrived
        # 1st, find the appointments already queued
        already = cls.search_read(
            [('appointment', 'in', map(int, appointments))],
            fields_names=['appointment', 'id'])
        alreadict = dict([(x['appointment'], x['id']) for x in already])
        vals = [{'appointment': a.id, 'priority': APM.get(a.urgency, 0),
                 'busy': False}
                for a in appointments if a.id not in alreadict]
        cls.create(vals)

    def get_visit_reason(self, name):
        '''get reason for visit'''
        if self.appointment:
            self.appointment.visit_reason
        return None


class QueueEntryNote(ModelView, ModelSQL):
    'Line Note'
    __name__ = 'gnuhealth.patient.queue_entry_note'
    queue_entry = fields.Many2One('gnuhealth.patient.queue_entry',
                                  'Queue Entry', required=True)
    note = fields.Text('Note', required=True)
    created = fields.Function(fields.DateTime('Created at'), 'get_writeinfo')
    creator = fields.Function(fields.Char('Creator'), 'get_writeinfo')
    byline = fields.Function(fields.Char('By Line'), 'get_writeinfo')

    @classmethod
    def __setup__(cls):
        super(QueueEntryNote, cls).__setup__()
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
            conv = lambda x: (x.id, u'%s at %s' % (
                              x.create_uid.name,
                              x.create_date.strftime('%H:%M on %Y-%m-%d')
                              ))
        else:
            conv = lambda x: (x.id, None)
        return dict(map(conv, instances))
