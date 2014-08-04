mailagent
=========

a smtp script for sending email weekly on a specified weekday

Author: sgleilei@gmail.com
License: BSD

change settings in setting.py, some details:
- smtp_bcc_sender # set True to BCC sender self
- smtp_attachments # specify attachment files
- smtp_schedule_skipdates # skip date periods 
  on ('<startmonth>-<day>', '<endmonth>-<day>') format

also not forget to set your smtp server and account in
mailagent.send_mail() function;

you need a linux-crontab like environment to invoke it daily;

run manually with
% python mailgent.py
