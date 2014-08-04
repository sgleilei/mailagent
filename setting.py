#!/usr/bin/env python
# coding=utf-8

import time

smtp_enable = True

smtp_bcc_sender = True

smtp_receivers = (
    'aaa@xxx.com',
    'bbb@yyy.com',
    'ccc@zzz.com'
)

def smtp_subject():
    return u'this is an email subject.'

def smtp_context():
    return u'''
Fellows:
    hello all!

%s
''' %time.strftime('--%Y-%m-%d--')

smtp_attachments = ()

smtp_schedule_weekday = 6 # 0-Sun, 1-Mon, 2-Tue, ..., 6-Sat

smtp_schedule_skipdates = (('5-1', '5-3'), ('10-1', '10-7'), ('1-10', '2-25'))
