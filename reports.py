"""This file stores the report models for health_traige_queue"""
#############################
# Author: Randy Burrell     #
# Date: 2016/10/11          #
#                           #
# Description: This file    #
# stores the report models  #
# for health_traige_queue   #
#############################

# from datetime import datetime, timedelta
# import pytz
# from trytond.pyson import Eval, PYSONEncoder, Date
# from trytond.transaction import Transaction
# from trytond.pool import Pool
from trytond.report import Report

__all__ = ('TriageReport')

class TriageReport(Report):
    '''This class is used to create reports for triaged patients'''
    __name__ = 'gnuhealth.triage.entry.report'
