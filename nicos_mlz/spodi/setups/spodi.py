description = 'SPODI setup'

group = 'basic'

includes = [
    'system', 'sampletable', 'detector', 'nguide', 'slits', 'filter',
    'mono', 'reactor'
]

# caress@spodictrl:/opt/caress>./dump_u1 bls
# BLS: OMGS=(-360,360) TTHS=(-3.1,160) OMGM=(40,80) CHIM=(-3,3) XM=(-15,15)
# YM=(-15,15) ZM=(0,220) SLITM_U=(-31,85) SLITM_D=(-85,31) SLITM_L=(-15.2,15.2)
# SLITM_R=(-15.2,15.2) SLITS_U=(0,45) SLITS_D=(-45,0) SLITS_L=(-15,0)
# SLITS_R=(0,15) POSH=(0,78) EXT=(-5,5) LOAD=(-50000,50000) CHIT=(-180,180)
# TEPOS=(-20,50) TEEXT=(-1000,3000) TELOAD=(-50000,50000) TOPOS=(-360,360)
# TOMOM=(1000,1000) SAMS=(-360,360) SAMR=(-360,360) XS=(-15,15) YS=(-15,15)
# ZS=(-20,20)
# caress@spodictrl:/opt/caress>./dump_u1 sof
# SOF: OMGS=-2735.92 TTHS=-1044.04 OMGM=-792.677 CHIM=2928.3 XM=-5852.43
# YM=-2043.89 ZM=-6347.84 SLITM_U=0 SLITM_D=0 SLITM_L=0 SLITM_R=0 SLITS_U=0
# SLITS_D=0 SLITS_L=0 SLITS_R=0 POSH=0 EXT=0 LOAD=0 CHIT=0 TEPOS=0 TEEXT=0
# TELOAD=0 TOPOS=0 TOMOM=0 SAMS=38573.1 SAMR=0 XS=0 YS=0 ZS=0

devices = dict(
    wav = device('nicos.devices.generic.ManualMove',
        description = 'Monochromator wavelength',
        unit = 'AA',
        abslimits = (1, 2.6),
    ),
)
