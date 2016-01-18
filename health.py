
from trytond.pool import Pool
from trytond.model import ModelSQL, ModelView, fields
from trytond.pyson import Eval

APM = {'a': 0, 'b': 2, 'c': 4}  # Appointment Priority Map


class Appointment(ModelSQL, ModelView):
    '''Appointment
    represents an appointment that a patient may have/be given to see
    a physician at this facility'''
    __name__ = 'gnuhealth.appointment'

    queue_entry = fields.One2Many('gnuhealth.patient.queue_entry',
                                  'appointment', 'Queue Entry', size=1)

    @classmethod
    def write(cls, records, values):
        # update queue item priority if necessary
        prio_ids = []
        if 'urgency' in values:
            prio_ids = map(int, records)
            prio = APM.get(values['urgency'])

        retval = super(Appointment, cls).write(records, values)
        if prio_ids:
            queue_model = Pool().get('gnuhealth.patient.queue_entry')
            qids = queue_model.search([('appointment', 'in', prio_ids)])
            queue_model.write(queue_model.browse(qids), {'priority': prio})
        return retval


class PatientEncounter(ModelSQL, ModelView):
    'Patient Encounter'
    __name__ = 'gnuhealth.encounter'

    queue_entry = fields.One2Many('gnuhealth.patient.queue_entry', 'encounter',
                                  'Queue Entry', size=1)

    @classmethod
    def create(cls, vlist):
        # attach the encounter to the same queue entry as the appointment
        appointment_ids = filter(None,
                                 [x.get('appointment', None) for x in vlist])
        if appointment_ids:
            queue_model = Pool().get('gnuhealth.patient.queue_entry')
            queue_entries = queue_model.search_read(
                [('appointment', 'in', appointment_ids),
                 ('encounter', '=', None)],
                fields_names=['appointment', 'id'])
            aq = dict([(k['appointment'], k['id']) for k in queue_entries])
        for vdict in vlist:
            vqentry = aq.get(vdict['appointment'], False)
            if vqentry:
                vdict['queue_entry'] = [('add', [vqentry])]
                # else:
                    # create the queue entry instead. why does it not exist?
                    # vdict['queue_entry'] = [('create',
                    #                          [{'appointment': vdict['appointment']}])]
        return super(PatientEncounter, cls).create(vlist)
