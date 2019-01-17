# -*- coding: utf-8 -*-

description = 'Email and SMS notifiers'

group = 'lowlevel'

devices = dict(
    email = device('nicos.devices.notifiers.Mailer',
        sender = 'spheres@frm2.tum.de',
        copies = [('s.rainow@fz-juelich.de', 'all')],
        subject = 'NICOS',
        mailserver = 'mailhost.frm2.tum.de',
    ),
    smser = device('nicos.devices.notifiers.SMSer',
        server = 'triton.admin.frm2',
        receivers = [],
    ),
)
