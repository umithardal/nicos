"""NICOS GUI default configuration."""

main_window = docked(
    vsplit(
        panel('status.ScriptStatusPanel'),
        # panel('watch.WatchPanel'),
        panel('console.ConsolePanel'),
    ),
    ('NICOS devices',
     panel('devices.DevicesPanel', icons=True, dockpos='right',)
    ),
    ('Experiment Information and Setup',
     panel('expinfo.ExpInfoPanel',)
    ),
)

windows = [
    window('Editor', 'editor', panel('editor.EditorPanel')),
    window('Scans', 'plotter', panel('scans.ScansPanel')),
    window('History', 'find', panel('history.HistoryPanel')),
    window('Logbook', 'table', panel('elog.ELogPanel')),
    window('Log files', 'table', panel('logviewer.LogViewerPanel')),
    window('Errors', 'errors', panel('errors.ErrorPanel')),
    #window('Live data', 'live', panel('live.LiveDataPanel')),
]

tools = [
    tool('Calculator', 'calculator.CalculatorTool'),
    tool('Neutron cross-sections', 'website.WebsiteTool',
         url='http://www.ncnr.nist.gov/resources/n-lengths/'),
    tool('Report NICOS bug or request enhancement', 'bugreport.BugreportTool'),
    tool('Emergency stop button', 'estop.EmergencyStopTool',
         runatstartup=False),
]
