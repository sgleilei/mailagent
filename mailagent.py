#!/usr/bin/env python
# coding=utf-8

import sys, os, time, datetime, smtplib, setting
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders
from email.Header import Header


g_coding = 'utf-8'


class Log(object):
	def __init__(self, log_file):
		self.log_file = log_file
		with open(self.log_file, 'r') as fd: lines = fd.readlines()
		if len(lines) > 0: self.last_line = lines[-1].strip()
		else: self.last_line = None
		return

	def append(self, text):
		with open(self.log_file, 'a') as fd:
			fd.write('%s|%s\n' %(time.strftime('%Y-%m-%d'), text.encode(g_coding)))
		return


g_scheduled = Log('scheduled.txt')
g_error_log = Log('error.txt')


def log_exception(e):
	exc_tb = sys.exc_info()[2]
	fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
	g_error_log.append('%s: %s in line %s' %(fname, repr(e), exc_tb.tb_lineno))
	return


def last_scheduled_date():
	last_line = g_scheduled.last_line
	if last_line == None: return datetime.date(2014, 1, 1)

	try:
		temp = last_line.split('|')
		if len(temp) != 2 or temp[1] != 'OK': raise Exception('%s format error' %g_scheduled.log_file)
	
		result = time.strptime(temp[0], '%Y-%m-%d')
		return datetime.date(result.tm_year, result.tm_mon, result.tm_mday)
	except Exception as e:
		log_exception(e)
		raise e
	return
	

def _send_mail(server, sender, send_from, send_to, subject, context, attachments, bcc_sender):
	result = False
	try:
		msg = MIMEMultipart()
		msg['From'] = send_from
		msg['To'] = COMMASPACE.join(send_to)
		if bcc_sender:
			msg["Bcc"] = send_from
			send_to = list(send_to)
			send_to.append(send_from)
		msg['Date'] = formatdate(localtime=True)
		msg['Subject'] = Header(subject, g_coding)
		msg.attach(MIMEText(context, 'plain', g_coding))

		for f in attachments:
			part = MIMEBase('application', "octet-stream")
			with open(f, 'rb') as fd: part.set_payload(fd.read())
			Encoders.encode_base64(part)
			part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(f))
			msg.attach(part)

		smtp = smtplib.SMTP_SSL()
		smtp.connect(server[0], server[1])
		smtp.login(sender[0], sender[1])
		smtp.sendmail(send_from, send_to, msg.as_string())
		result = True
	except Exception, e:
		log_exception(e)
	finally:
		try: smtp.close()
		except: pass
	return result


def send_mail():
	server = ('smtp_server_domain', 465) # port 465 is for SSL connection
	sender = ('your_smtp_account', 'your_smtp_password')
	send_from = sender[0]
	send_to = setting.smtp_receivers
	subject = setting.smtp_subject().encode(g_coding)
	context = setting.smtp_context().encode(g_coding)
	attachs = setting.smtp_attachments
	return _send_mail(server, sender, send_from, send_to, subject, context, attachs, setting.smtp_bcc_sender)


def is_festival(today):
	return False


def within_a_week(last, today):
	return (today - last).days < 7


def within_a_duration(start, end, today):
	return (today - start).days >= 0 and (end - today).days >= 0


def schedule_run():
	if not setting.smtp_enable: return

	today = datetime.date.today()
	for p in setting.smtp_schedule_skipdates:
		d1 = time.strptime(p[0], '%m-%d')
		d1 = datetime.date(today.year, d1.tm_mon, d1.tm_mday)
		d2 = time.strptime(p[1], '%m-%d')
		d2 = datetime.date(today.year, d2.tm_mon, d2.tm_mday)
		if within_a_duration(d1, d2, today): return

	if is_festival(today): return
	
	last_date = last_scheduled_date()
	delta_weekday = last_date.weekday() - setting.smtp_schedule_weekday
	if delta_weekday < 0: delta_weekday += 7
	# convert to the day of a week start
	last = last_date - datetime.timedelta(days=delta_weekday)

	if within_a_week(last, today):
		#fetch mail reply here
		pass
	else:
		# now exceed a week since last sent
		if send_mail(): g_scheduled.append('OK')
	return


if __name__ == '__main__':
	schedule_run()
