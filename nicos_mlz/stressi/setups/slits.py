description = 'Primary slit CARESS HWB Devices'

group = 'lowlevel'

servername = 'VME'

nameservice = 'stressictrl.stressi.frm2'

excludes = ['motorbox01']
includes = ['mux']

devices = dict(
    slits_u = device('nicos.devices.vendor.caress.MuxMotor',
        description = 'HWB SLITS_U',
        fmtstr = '%.2f',
        unit = 'mm',
        coderoffset = -0,
        abslimits = (-10, 43),
        nameserver = '%s' % nameservice,
        objname = '%s' % servername,
        config = 'SLITS_U 39 3 1 13 100.0 20 80',
        lowlevel = True,
        pollinterval = 60,
        maxage = 90,
        mux = 'mux',
    ),
    slits_d = device('nicos.devices.vendor.caress.MuxMotor',
        description = 'HWB SLITS_D',
        fmtstr = '%.2f',
        unit = 'mm',
        coderoffset = 0,
        abslimits = (-43, 10),
        userlimits = (-43, 10),
        nameserver = '%s' % nameservice,
        objname = '%s' % servername,
        config = 'SLITS_D 39 3 1 14 -100.0 20 80',
        lowlevel = True,
        pollinterval = 60,
        maxage = 90,
        mux = 'mux',
    ),
    slits_l = device('nicos.devices.vendor.caress.MuxMotor',
        description = 'HWB SLITS_L',
        fmtstr = '%.2f',
        unit = 'mm',
        coderoffset = 0,
        abslimits = (-26, 10),
        userlimits = (-26, 10),
        nameserver = '%s' % nameservice,
        objname = '%s' % servername,
        config = 'SLITS_L 39 3 1 15 -100.0 20 80',
        lowlevel = True,
        pollinterval = 60,
        maxage = 90,
        mux = 'mux',
    ),
    slits_r = device('nicos.devices.vendor.caress.MuxMotor',
        description = 'HWB SLITS_R',
        fmtstr = '%.2f',
        unit = 'mm',
        coderoffset = 0,
        abslimits = (-10, 26),
        nameserver = '%s' % nameservice,
        objname = '%s' % servername,
        config = 'SLITS_R 39 3 1 16 100.0 20 80',
        lowlevel = True,
        pollinterval = 60,
        maxage = 90,
        mux = 'mux',
    ),
    slits = device('nicos_mlz.stressi.devices.slit.Slit',
        description = 'sample slit 4 blades',
        left = 'slits_l',
        right = 'slits_r',
        bottom = 'slits_d',
        top = 'slits_u',
        opmode = 'centered',
        pollinterval = 60,
        maxage = 90,
    ),
    slitm_w = device('nicos.devices.vendor.caress.MuxMotor',
        description = 'HWB SLITM_W',
        fmtstr = '%.2f',
        unit = 'mm',
        coderoffset = 0,
        abslimits = (0, 100),
        nameserver = '%s' % nameservice,
        objname = '%s' % servername,
        config = 'SLITM_W 39 3 1 10 100.0 20 80',
        lowlevel = True,
        pollinterval = 60,
        maxage = 90,
        mux = 'mux',
    ),
    slitm_h = device('nicos.devices.vendor.caress.MuxMotor',
        description = 'HWB SLITM_H',
        fmtstr = '%.2f',
        unit = 'mm',
        coderoffset = 0,
        abslimits = (0, 155),
        nameserver = '%s' % nameservice,
        objname = '%s' % servername,
        config = 'SLITM_H 39 3 1 11 100.0 20 80',
        lowlevel = True,
        pollinterval = 60,
        maxage = 90,
        mux = 'mux',
    ),
    slitm = device('nicos_mlz.stressi.devices.slit.TwoAxisSlit',
        description = 'Monochromator entry slit',
        horizontal = 'slitm_w',
        vertical = 'slitm_h',
        pollinterval = 60,
        maxage = 90,
    ),
    slite = device('nicos.devices.vendor.caress.MuxMotor',
        description = 'HWB SLITE',
        fmtstr = '%.2f',
        unit = 'mm',
        coderoffset = 0,
        abslimits = (0, 70),
        nameserver = '%s' % nameservice,
        objname = '%s' % servername,
        config = 'SLITM_E 39 3 1 12 100.0 20 80',
        pollinterval = 60,
        maxage = 90,
        mux = 'mux',
    ),
)
