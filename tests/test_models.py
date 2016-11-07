"""Automated tests"""
#!/usr/bin/env python

import os
import sys
import doctest
import unittest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import test_view, test_depends 
                                       # doctest_setup, doctest_teardown)

DIR = os.path.abspath(os.path.normpath(os.path.join(__file__,
                                                    '..', '..', 
                                                    '..', '..', 
                                                    '..', 'trytond')))
if os.path.isdir(DIR):
    sys.path.insert(0, os.path.dirname(DIR))



class TriageQueueViewTestCase(unittest.TestCase):
    '''
    Test Health_Triage_Queue module.
    '''

    def setUp(self):
        trytond.tests.test_tryton.install_module('health_triage_queue')

    def test0001views(self):
        '''
        Test views.
        '''
        test_view('health_triage_queue')

    def test0002depends(self):
        '''
        Test depends.
        '''
        test_depends()

def suite():
    """Test suites"""
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        TriageQueueViewTestCase))
    suite.addTests(doctest.DocFileSuite('test_queue.rst',
                                        setUp=None, 
                                        tearDown=None, 
                                        encoding='utf-8', 
                                        optionflags=doctest.REPORT_ONLY_FIRST_FAILURE,
                                        checker=None))
    suite.addTests(doctest.DocFileSuite('test_queue_called_by_me.rst',
                                        setUp=None, 
                                        tearDown=None, 
                                        encoding='utf-8', 
                                        optionflags=doctest.REPORT_ONLY_FIRST_FAILURE,
                                        checker=None))
    suite.addTests(doctest.DocFileSuite('test_queue_called_by.rst',
                                        setUp=None, 
                                        tearDown=None, 
                                        encoding='utf-8', 
                                        optionflags=doctest.REPORT_ONLY_FIRST_FAILURE,
                                        checker=None))
    suite.addTests(doctest.DocFileSuite('test_queue_encounter_components.rst',
                                        setUp=None, 
                                        tearDown=None, 
                                        encoding='utf-8', 
                                        optionflags=doctest.REPORT_ONLY_FIRST_FAILURE,
                                        checker=None))
    suite.addTests(doctest.DocFileSuite('test_queue_encounter_component_count.rst',
                                        setUp=None, 
                                        tearDown=None, 
                                        encoding='utf-8', 
                                        optionflags=doctest.REPORT_ONLY_FIRST_FAILURE,
                                        checker=None))
    suite.addTests(doctest.DocFileSuite('test_queue_entry_state.rst',
                                        setUp=None, 
                                        tearDown=None, 
                                        encoding='utf-8', 
                                        optionflags=doctest.REPORT_ONLY_FIRST_FAILURE,
                                        checker=None))
    suite.addTests(doctest.DocFileSuite('test_queue_triage_status.rst',
                                        setUp=None, 
                                        tearDown=None, 
                                        encoding='utf-8', 
                                        optionflags=doctest.REPORT_ONLY_FIRST_FAILURE,
                                        checker=None))
    suite.addTests(doctest.DocFileSuite('test_queue_name.rst',
                                        setUp=None, 
                                        tearDown=None, 
                                        encoding='utf-8', 
                                        optionflags=doctest.REPORT_ONLY_FIRST_FAILURE,
                                        checker=None))
    suite.addTests(doctest.DocFileSuite('test_queue_upi_mrn_id.rst',
                                        setUp=None, 
                                        tearDown=None, 
                                        encoding='utf-8', 
                                        optionflags=doctest.REPORT_ONLY_FIRST_FAILURE,
                                        checker=None))
    suite.addTests(doctest.DocFileSuite('test_queue_sex.rst',
                                        setUp=None, 
                                        tearDown=None, 
                                        encoding='utf-8', 
                                        optionflags=doctest.REPORT_ONLY_FIRST_FAILURE,
                                        checker=None))
    suite.addTests(doctest.DocFileSuite('test_queue_age.rst',
                                        setUp=None, 
                                        tearDown=None, 
                                        encoding='utf-8', 
                                        optionflags=doctest.REPORT_ONLY_FIRST_FAILURE,
                                        checker=None))
    suite.addTests(doctest.DocFileSuite('test_queue_primary_complaint.rst',
                                        setUp=None, 
                                        tearDown=None, 
                                        encoding='utf-8', 
                                        optionflags=doctest.REPORT_ONLY_FIRST_FAILURE,
                                        checker=None))
    suite.addTests(doctest.DocFileSuite('test_queue_notes.rst',
                                        setUp=None, 
                                        tearDown=None, 
                                        encoding='utf-8', 
                                        optionflags=doctest.REPORT_ONLY_FIRST_FAILURE,
                                        checker=None))
    suite.addTests(doctest.DocFileSuite('test_queue_last_touch.rst',
                                        setUp=None, 
                                        tearDown=None, 
                                        encoding='utf-8', 
                                        optionflags=doctest.REPORT_ONLY_FIRST_FAILURE,
                                        checker=None))
    suite.addTests(doctest.DocFileSuite('test_queue_last_toucher.rst',
                                        setUp=None, 
                                        tearDown=None, 
                                        encoding='utf-8', 
                                        optionflags=doctest.REPORT_ONLY_FIRST_FAILURE,
                                        checker=None))
    suite.addTests(doctest.DocFileSuite('test_queue_specialty.rst',
                                        setUp=None, 
                                        tearDown=None, 
                                        encoding='utf-8', 
                                        optionflags=doctest.REPORT_ONLY_FIRST_FAILURE,
                                        checker=None))
    suite.addTests(doctest.DocFileSuite('test_queue_timehere.rst',
                                        setUp=None, 
                                        tearDown=None, 
                                        encoding='utf-8', 
                                        optionflags=doctest.REPORT_ONLY_FIRST_FAILURE,
                                        checker=None))
    suite.addTests(doctest.DocFileSuite('test_queue_visit_reason.rst',
                                        setUp=None, 
                                        tearDown=None, 
                                        encoding='utf-8', 
                                        optionflags=doctest.REPORT_ONLY_FIRST_FAILURE,
                                        checker=None))
    suite.addTests(doctest.DocFileSuite('test_triage.rst',
                                        setUp=None, 
                                        tearDown=None, 
                                        encoding='utf-8', 
                                        optionflags=doctest.REPORT_ONLY_FIRST_FAILURE,
                                        checker=None))
    suite.addTests(doctest.DocFileSuite('test_triage_done.rst',
                                        setUp=None, 
                                        tearDown=None, 
                                        encoding='utf-8', 
                                        optionflags=doctest.REPORT_ONLY_FIRST_FAILURE,
                                        checker=None))
    suite.addTests(doctest.DocFileSuite('test_triage_function_field_child_bearing_age.rst',
                                        setUp=None, 
                                        tearDown=None, 
                                        encoding='utf-8', 
                                        optionflags=doctest.REPORT_ONLY_FIRST_FAILURE,
                                        checker=None))
    suite.addTests(doctest.DocFileSuite('test_triage_sex_display.rst',
                                        setUp=None, 
                                        tearDown=None, 
                                        encoding='utf-8', 
                                        optionflags=doctest.REPORT_ONLY_FIRST_FAILURE,
                                        checker=None))
    suite.addTests(doctest.DocFileSuite('test_triage_age_display.rst',
                                        setUp=None, 
                                        tearDown=None, 
                                        encoding='utf-8', 
                                        optionflags=doctest.REPORT_ONLY_FIRST_FAILURE,
                                        checker=None))
    suite.addTests(doctest.DocFileSuite('test_triage_id_display.rst',
                                        setUp=None, 
                                        tearDown=None, 
                                        encoding='utf-8', 
                                        optionflags=doctest.REPORT_ONLY_FIRST_FAILURE,
                                        checker=None))
    suite.addTests(doctest.DocFileSuite('test_triage_medical_alert.rst',
                                        setUp=None, 
                                        tearDown=None, 
                                        encoding='utf-8', 
                                        optionflags=doctest.REPORT_ONLY_FIRST_FAILURE,
                                        checker=None))
    suite.addTests(doctest.DocFileSuite('test_triage_status_display.rst',
                                        setUp=None, 
                                        tearDown=None, 
                                        encoding='utf-8', 
                                        optionflags=doctest.REPORT_ONLY_FIRST_FAILURE,
                                        checker=None))
    suite.addTests(doctest.DocFileSuite('test_triage_note_display.rst',
                                        setUp=None, 
                                        tearDown=None, 
                                        encoding='utf-8', 
                                        optionflags=doctest.REPORT_ONLY_FIRST_FAILURE,
                                        checker=None))
    suite.addTests(doctest.DocFileSuite('test_triage_upi.rst',
                                        setUp=None, 
                                        tearDown=None, 
                                        encoding='utf-8', 
                                        optionflags=doctest.REPORT_ONLY_FIRST_FAILURE,
                                        checker=None))
    suite.addTests(doctest.DocFileSuite('test_triage_name.rst',
                                        setUp=None, 
                                        tearDown=None, 
                                        encoding='utf-8', 
                                        optionflags=doctest.REPORT_ONLY_FIRST_FAILURE,
                                        checker=None))
    suite.addTests(doctest.DocFileSuite('test_triage_patient_search.rst',
                                        setUp=None, 
                                        tearDown=None, 
                                        encoding='utf-8', 
                                        optionflags=doctest.REPORT_ONLY_FIRST_FAILURE,
                                        checker=None))
    suite.addTests(doctest.DocFileSuite('test_triage_can_do_details.rst',
                                        setUp=None, 
                                        tearDown=None, 
                                        encoding='utf-8', 
                                        optionflags=doctest.REPORT_ONLY_FIRST_FAILURE,
                                        checker=None))
    suite.addTests(doctest.DocFileSuite('test_triage_first_contact_time.rst',
                                        setUp=None, 
                                        tearDown=None, 
                                        encoding='utf-8', 
                                        optionflags=doctest.REPORT_ONLY_FIRST_FAILURE,
                                        checker=None))
    suite.addTests(doctest.DocFileSuite('test_triage_total_time.rst',
                                        setUp=None, 
                                        tearDown=None, 
                                        encoding='utf-8', 
                                        optionflags=doctest.REPORT_ONLY_FIRST_FAILURE,
                                        checker=None))
    suite.addTests(doctest.DocFileSuite('test_triage_note_entries.rst',
                                        setUp=None, 
                                        tearDown=None, 
                                        encoding='utf-8', 
                                        optionflags=doctest.REPORT_ONLY_FIRST_FAILURE,
                                        checker=None))
    suite.addTests(doctest.DocFileSuite('test_triage_note_created.rst',
                                        setUp=None, 
                                        tearDown=None, 
                                        encoding='utf-8', 
                                        optionflags=doctest.REPORT_ONLY_FIRST_FAILURE,
                                        checker=None))
    suite.addTests(doctest.DocFileSuite('test_triage_note_creator.rst',
                                        setUp=None, 
                                        tearDown=None, 
                                        encoding='utf-8', 
                                        optionflags=doctest.REPORT_ONLY_FIRST_FAILURE,
                                        checker=None))
    suite.addTests(doctest.DocFileSuite('test_triage_note_byline.rst',
                                        setUp=None, 
                                        tearDown=None, 
                                        encoding='utf-8', 
                                        optionflags=doctest.REPORT_ONLY_FIRST_FAILURE,
                                        checker=None))
    suite.addTests(doctest.DocFileSuite('test_referral.rst',
                                        setUp=None, 
                                        tearDown=None, 
                                        encoding='utf-8', 
                                        optionflags=doctest.REPORT_ONLY_FIRST_FAILURE,
                                        checker=None))
    suite.addTests(doctest.DocFileSuite('test_referral_sex.rst',
                                        setUp=None, 
                                        tearDown=None, 
                                        encoding='utf-8', 
                                        optionflags=doctest.REPORT_ONLY_FIRST_FAILURE,
                                        checker=None))
    suite.addTests(doctest.DocFileSuite('test_referral_sex_display.rst',
                                        setUp=None, 
                                        tearDown=None, 
                                        encoding='utf-8', 
                                        optionflags=doctest.REPORT_ONLY_FIRST_FAILURE,
                                        checker=None))
    suite.addTests(doctest.DocFileSuite('test_referral_puid.rst',
                                        setUp=None, 
                                        tearDown=None, 
                                        encoding='utf-8', 
                                        optionflags=doctest.REPORT_ONLY_FIRST_FAILURE,
                                        checker=None))
    suite.addTests(doctest.DocFileSuite('test_referral_age.rst',
                                        setUp=None, 
                                        tearDown=None, 
                                        encoding='utf-8', 
                                        optionflags=doctest.REPORT_ONLY_FIRST_FAILURE,
                                        checker=None))
    suite.addTests(doctest.DocFileSuite('test_referral_dob.rst',
                                        setUp=None, 
                                        tearDown=None, 
                                        encoding='utf-8', 
                                        optionflags=doctest.REPORT_ONLY_FIRST_FAILURE,
                                        checker=None))
    suite.addTests(doctest.DocFileSuite('test_referral_is_local.rst',
                                        setUp=None, 
                                        tearDown=None, 
                                        encoding='utf-8', 
                                        optionflags=doctest.REPORT_ONLY_FIRST_FAILURE,
                                        checker=None))
    suite.addTests(doctest.DocFileSuite('test_referral_is_target.rst',
                                        setUp=None, 
                                        tearDown=None, 
                                        encoding='utf-8', 
                                        optionflags=doctest.REPORT_ONLY_FIRST_FAILURE,
                                        checker=None))
    suite.addTests(doctest.DocFileSuite('test_referral_signed_local.rst',
                                        setUp=None, 
                                        tearDown=None, 
                                        encoding='utf-8', 
                                        optionflags=doctest.REPORT_ONLY_FIRST_FAILURE,
                                        checker=None))
    suite.addTests(doctest.DocFileSuite('test_referral_signed_target.rst',
                                        setUp=None, 
                                        tearDown=None, 
                                        encoding='utf-8', 
                                        optionflags=doctest.REPORT_ONLY_FIRST_FAILURE,
                                        checker=None))
    suite.addTests(doctest.DocFileSuite('test_referral_signed_local_button.rst',
                                        setUp=None, 
                                        tearDown=None, 
                                        encoding='utf-8', 
                                        optionflags=doctest.REPORT_ONLY_FIRST_FAILURE,
                                        checker=None))
    suite.addTests(doctest.DocFileSuite('test_referral_signed_target_button.rst',
                                        setUp=None, 
                                        tearDown=None, 
                                        encoding='utf-8', 
                                        optionflags=doctest.REPORT_ONLY_FIRST_FAILURE,
                                        checker=None))
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
