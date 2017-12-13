description = 'Slits'

group = 'lowlevel'

servername = 'VMESPODI'

nameservice = 'spodisrv.spodi.frm2'

includes = ['mux']

# MUX modules (attention: velo and accel in steps per s, CARESS converts these
# natural unit into the obscure ST180 unit)
# name kind mux lun motor# ratio velo accel e_fac e_lim

devices = dict(
    # Monochromator slit
    # slitm_u = device('nicos.devices.vendor.caress.MuxMotor',
    #     description = 'HWB SLITM_U',
    #     fmtstr = '%.2f',
    #     unit = 'mm',
    #     coderoffset = 0,
    #     abslimits = (-31, 85),
    #     nameserver = '%s' % nameservice,
    #     objname = '%s' % servername,
    #     config = 'SLITM_U 39 3 1 1 10000 500 200 5.12 60',
    #     lowlevel = True,
    #     mux = 'mux',
    # ),
    # slitm_d = device('nicos.devices.vendor.caress.MuxMotor',
    #     description = 'HWB SLITM_D',
    #     fmtstr = '%.2f',
    #     unit = 'mm',
    #     coderoffset = 0,
    #     abslimits = (-85, 31),
    #     nameserver = '%s' % nameservice,
    #     objname = '%s' % servername,
    #     config = 'SLITM_D 39 3 1 2 10000 500 200 5.12 60',
    #     lowlevel = True,
    #     mux = 'mux',
    # ),
    # slitm_l = device('nicos.devices.vendor.caress.MuxMotor',
    #     description = 'HWB SLITM_L',
    #     fmtstr = '%.2f',
    #     unit = 'mm',
    #     coderoffset = 0,
    #     abslimits = (-15.2, 15.2),
    #     nameserver = '%s' % nameservice,
    #     objname = '%s' % servername,
    #     config = 'SLITM_L 39 3 1 3 1000 500 200 5.12 30',
    #     lowlevel = True,
    #     mux = 'mux',
    # ),
    # slitm_r = device('nicos.devices.vendor.caress.MuxMotor',
    #     description = 'HWB SLITM_R',
    #     fmtstr = '%.2f',
    #     unit = 'mm',
    #     coderoffset = 0,
    #     abslimits = (-15.2, 15.2),
    #     nameserver = '%s' % nameservice,
    #     objname = '%s' % servername,
    #     config = 'SLITM_R 39 3 1 4 1000 500 200 5.12 30',
    #     lowlevel = True,
    #     mux = 'mux',
    # ),
    # slitm = device('nicos_mlz.stressi.devices.slit.Slit',
    #     description = 'Monochromator slit 4 blades',
    #     left = 'slits_l',
    #     right = 'slits_r',
    #     bottom = 'slits_d',
    #     top = 'slits_u',
    #     opmode = 'centered',
    #     pollinterval = 60,
    #     maxage = 90,
    # ),
    slits_u = device('nicos.devices.vendor.caress.MuxMotor',
        description = 'HWB SLITS_U',
        fmtstr = '%.2f',
        unit = 'mm',
        coderoffset = -0,
        abslimits = (0, 45),
        nameserver = '%s' % nameservice,
        objname = '%s' % servername,
        config = 'SLITS_U 39 3 1 5 1000. 20 80',
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
        abslimits = (-45, 0),
        nameserver = '%s' % nameservice,
        objname = '%s' % servername,
        config = 'SLITS_D 39 3 1 6 1000. 20 80',
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
        abslimits = (-15, 0),
        nameserver = '%s' % nameservice,
        objname = '%s' % servername,
        config = 'SLITS_L 39 3 1 7 1000. 20 80',
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
        abslimits = (0, 15),
        nameserver = '%s' % nameservice,
        objname = '%s' % servername,
        config = 'SLITS_R 39 3 1 8 1000. 20 80',
        lowlevel = True,
        pollinterval = 60,
        maxage = 90,
        mux = 'mux',
    ),
    slits = device('nicos_mlz.stressi.devices.slit.Slit',
        description = 'Sample slit 4 blades',
        left = 'slits_l',
        right = 'slits_r',
        bottom = 'slits_d',
        top = 'slits_u',
        opmode = 'centered',
        pollinterval = 60,
        maxage = 90,
    ),
)
