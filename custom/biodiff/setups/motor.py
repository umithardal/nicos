# -*- coding: utf-8 -*-

description = "Axes setup"
group = "lowlevel"

tango_base = "tango://phys.biodiff.frm2:10000/biodiff/"

devices = dict(
    omega_samplestepper = device("devices.tango.Motor",
                                 description = "Sample stepper omega variant",
                                 tangodevice = tango_base +
                                               "fzjs7/omega_samplestepper",
                                 unit = "deg",
                                 precision = 0.001,
                                ),
    omega_sampletable = device("devices.tango.Motor",
                               description = "Sample table omega variant",
                               tangodevice = tango_base + "fzjs7/omega_sampletable",
                               unit = "deg",
                               precision = 0.001,
                              ),
    x_sampletable = device("devices.tango.Motor",
                           description = "Sample table x axis",
                           tangodevice = tango_base + "fzjs7/x_sampletable",
                           unit = "mm",
                           precision = 0.005,
                          ),
    y_sampletable = device("devices.tango.Motor",
                           description = "Sample table y axis",
                           tangodevice = tango_base + "fzjs7/y_sampletable",
                           unit = "mm",
                           precision = 0.005,
                          ),
    z_sampletable = device("devices.tango.Motor",
                           description = "Sample table x axis",
                           tangodevice = tango_base + "fzjs7/z_sampletable",
                           unit = "mm",
                           precision = 0.005,
                          ),
    theta_monochromator = device("devices.tango.Motor",
                                 description = "Monochromator theta variant",
                                 tangodevice = tango_base +
                                               "fzjs7/theta_monochromator",
                                 unit = "deg",
                                 precision = 0.001,
                                ),
    tilt_monochromator = device("devices.tango.Motor",
                                description = "Monochromator tilt",
                                tangodevice = tango_base + "fzjs7/tilt_monochromator",
                                unit = "deg",
                                precision = 0.005,
                               ),
    x_monochromator = device("devices.tango.Motor",
                             description = "Monochromator x axis",
                             tangodevice = tango_base + "fzjs7/x_monochromator",
                             unit = "mm",
                             precision = 0.002,
                            ),
    y_monochromator = device("devices.tango.Motor",
                             description = "Monochromator y axis",
                             tangodevice = tango_base + "fzjs7/y_monochromator",
                             unit = "mm",
                             precision = 0.002,
                            ),
    z_monochromator = device("devices.tango.Motor",
                             description = "Monochromator z axis",
                             tangodevice = tango_base + "fzjs7/z_monochromator",
                             unit = "mm",
                             precision = 0.002,
                            ),
    theta2_selectorarm = device("devices.tango.Motor",
                                description = "Selector arm 2theta variant",
                                tangodevice = tango_base + "fzjs7/2theta_selectorarm",
                                unit = "deg",
                                precision = 0.005,
                               ),
    d_diaphragm1 = device("devices.tango.Motor",
                          description = "Slit 1",
                          tangodevice = tango_base + "fzjs7/d_diaphragm1",
                          unit = "mm",
                          precision = 0.05,
                         ),
    d_diaphragm2 = device("devices.tango.Motor",
                          description = "Slit 2",
                          tangodevice = tango_base + "fzjs7/d_diaphragm2",
                          unit = "mm",
                          precision = 0.05,
                         ),
    theta2_detectorunit = device("devices.tango.Motor",
                                 description = "Detector unit 2theta variant",
                                 tangodevice = tango_base +
                                               "fzjs7/2theta_detectorunit",
                                 unit = "deg",
                                 precision = 0.005,
                                ),
    z_imageplate = device("devices.tango.Motor",
                          description = "Neutron image plate z axis",
                          tangodevice = tango_base + "fzjs7/z_neutronimageplate",
                          unit = "mm",
                          precision = 0.01,
                         ),
    z_CCD = device("devices.tango.Motor",
                   description = "CCD z axis",
                   tangodevice = tango_base + "fzjs7/z_CCD",
                   unit = "mm",
                   precision = 0.01,
                  ),
    z_CCDcamera = device("devices.tango.Motor",
                         description = "CCD camera z axis",
                         tangodevice = tango_base + "fzjs7/z_CCDcamera",
                         unit = "mm",
                         precision = 0.01,
                        ),
    #theta2_CCDcamera = device("devices.tango.Motor",
    #                          description = "CCD camera 2theta variant",
    #                          tangodevice = tango_base + "fzjs7/2theta_CCDcamera",
    #                          unit = "deg",
    #                          precision = 0.01,
    #                         ),
    rot_scintillatorhead = device("biodiff.motor.S7InterlockMotor",
                                  description = "Scintillator head rotation",
                                  tangodevice = tango_base +
                                                "fzjs7/rot_scintillatorhead",
                                  unit = "deg",
                                  precision = 0.5,
                                 ),
#   omega_samplegoniometer = device("devices.tango.Motor",
#                                   description = "Sample goniometer " +
#                                                 "omega variant",
#                                   tangodevice = tango_base +
#                                                 "fzjs7/omega_samplegoniometer",
#                                  ),
#   x_samplegoniometer = device("devices.tango.Motor",
#                               description = "Sample goniometer x axis",
#                               tangodevice = tango_base + "fzjs7/x_samplegoniometer",
#                              ),
#   y_samplegoniometer = device("devices.tango.Motor",
#                               description = "Sample goniometer y axis",
#                               tangodevice = tango_base + "fzjs7/y_samplegoniometer",
#                              ),
#   rot_diaphragm3 = device("devices.tango.Motor",
#                           description = "Slit 3",
#                           tangodevice = tango_base + "fzjs7/rot_diaphragm3",
#                           unit = "deg",
#                          ),
#   rot_diaphragm4 = device("devices.tango.Motor",
#                           description = "Slit 4",
#                           tangodevice = tango_base + "fzjs7/rot_diaphragm4",
#                           unit = "deg",
#                          ),
)
