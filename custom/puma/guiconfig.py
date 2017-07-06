"""NICOS GUI default configuration."""

main_window = docked (
        vsplit('Console',
                panel('console.ConsolePanel'),
        ),
        ('Script',
                panel('status.ScriptStatusPanel'),
#               panel('watch.WatchPanel'),
        ),
        ('NICOS Devices',
                panel('devices.DevicesPanel'),
        ),
)

windows = [
        window('Setup', 'setup',
            tabbed(('Experiment', panel('setup_panel.ExpPanel')),
                   ('Setups',     panel('setup_panel.SetupsPanel')),
                   ('Detectors/Environment', panel('setup_panel.DetEnvPanel')),
            )),
        window('Editor', 'editor',
            vsplit(
                panel('scriptbuilder.CommandsPanel'),
                panel('editor.EditorPanel',
                  tools = [
                      tool('Scan', 'scan.ScanTool')
                  ]))),
        window('Scans', 'plotter',
            panel('scans.ScansPanel')),
        window('History', 'find',
            panel('history.HistoryPanel')),
        window('Logbook', 'table',
            panel('elog.ELogPanel')),
        window('Errors', 'errors',
            panel('errors.ErrorPanel')),
        window('Live data', 'live',
            panel('live.LiveDataPanel')),
        window('TAS status', 'table',
            panel('generic.GenericPanel',
                  uifile='custom/demo/lib/gui/tasaxes.ui')),
]

tools = [
    tool('Downtime report', 'downtime.DownTimeTool',
         receiver='f.carsughi@fz-juelich.de',
         mailserver='smtp.frm2.tum.de',
         sender='puma@frm2.tum.de',
    ),
    tool('Calculator', 'calculator.CalculatorTool'),
    tool('Neutron cross-sections', 'website.WebsiteTool',
         url='http://www.ncnr.nist.gov/resources/n-lengths/'),
    tool('Neutron activation', 'website.WebsiteTool',
         url='https://webapps.frm2.tum.de/intranet/activation/'),
    tool('Neutron calculations', 'website.WebsiteTool',
         url='https://webapps.frm2.tum.de/intranet/neutroncalc/'),
    tool('Report NICOS bug or request enhancement', 'bugreport.BugreportTool'),
]
