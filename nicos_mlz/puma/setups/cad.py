description = 'Combined multianalyzer axis setup'

group = 'lowlevel'

includes = ['analyser']

devices = dict(
    cad = device('nicos_mlz.puma.devices.PumaCoupledAxis',
        description = 'cad - combined axis for multianalyzer',
        tt = 'att_cad',
        th = 'ath',
        fmtstr = '%.3f',
        unit = 'deg',
        precision = 0.01,
	difflimit = 10.,
    ),
    att_cad = device('nicos.devices.generic.Axis',
        description = 'Scattering angle two-theta of analyser',
        motor = 'st_att',
        coder = 'co_att',
        precision = 0.01,
        offset = 90.205,  # 0.205, # 90.163 / 05.2017 GE
        jitter = 0.2,
        dragerror = 1,
        maxtries = 30,
	lowlevel = True,
    ),
)

startupcode = '''
resetlimits(att)
resetlimits(ath)
cad.tt.offset = 90
'''
