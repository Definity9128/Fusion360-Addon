import adsk.core
import traceback


try:
    from . import config
    from .apper import apper

    from .commands.PostProcess import PostProcess
    from .commands.ExportDXF import ExportDXF
    from .commands.GenerateGridlines import GenerateGridlines
    from .commands.CenterPunch import CenterPunch
    from .commands.SetupCreator import SetupCreator
    from .commands.AutoProjectEdges import AutoProjectEdges

    # Create our addin definition object
    my_addin = apper.FusionApp(config.app_name, config.company_name, False)
    my_addin.root_path = config.app_path

    # Add additional commands here

     #DESIGN ENVIROMENT BELOW
    
    my_addin.add_command(
        'Export DXF',
        ExportDXF,
        {
            'cmd_description': 'Export selected face to DXF file',
            'cmd_id': 'export_dxf',
            'workspace': 'FusionSolidEnvironment',
            'toolbar_panel_id': 'Export DXF',
            'cmd_resources': 'command_icons',
            'command_visible': True,
            'command_promoted': False,
        }
    )

    my_addin.add_command(
        'Relief Holes',
        CenterPunch,
        {
            'cmd_description': 'Select a face, then body. Command will create relief holes, 1 inline with the Center of Mass and numeriuos spanning out in an 8ft x 8ft grid',
            'cmd_id': 'CenterPunch',
            'workspace': 'FusionSolidEnvironment',
            'toolbar_panel_id': 'Relief Holes',
            'cmd_resources': 'command_icons',
            'command_visible': True,
            'command_promoted': False,
        }
    )
    
    my_addin.add_command(
        'Generate Gridlines',
        GenerateGridlines,
        {
            'cmd_description': 'Command generates gridlines on selected face. Note only works with rectangles',
            'cmd_id': 'generate_gridlines',
            'workspace': 'FusionSolidEnvironment',
            'toolbar_panel_id': 'Generate Gridlines',
            'cmd_resources': 'command_icons',
            'command_visible': True,
            'command_promoted': False,
        }
    )
    my_addin.add_command(
        'Project Selected Face',
        AutoProjectEdges,
        {
            'cmd_description': 'Command automatically projects selected face to a sketch on the same plane as selected face.',
            'cmd_id': 'AutoProjectEdges',
            'workspace': 'FusionSolidEnvironment',
            'toolbar_panel_id': 'Project Selected Face',
            'cmd_resources': 'command_icons',
            'command_visible': True,
            'command_promoted': False,
        }
    )

     #CAM ENVIROMENT BELOW

    my_addin.add_command(
        'Post Process',
        PostProcess,
        {
            'cmd_description': 'Post Job',
            'cmd_id': 'AXYZ Post',
            'workspace': 'CAMEnvironment',
            'toolbar_panel_id': 'Post Process',
            'cmd_resources': 'command_icons',
            'command_visible': True,
            'command_promoted': False,
        }
    )

    my_addin.add_command(
        'Setup Creator',
        SetupCreator,
        {
            'cmd_description': 'Create new Setup',
            'cmd_id': 'Setup Creator',
            'workspace': 'CAMEnvironment',
            'toolbar_panel_id': 'Setup Creator',
            'cmd_resources': 'command_icons',
            'command_visible': True,
            'command_promoted': False,
        }
    )
    app = adsk.core.Application.cast(adsk.core.Application.get())
    ui = app.userInterface

except:
    app = adsk.core.Application.get()
    ui = app.userInterface
    if ui:
        ui.messageBox('Initialization Failed: {}'.format(traceback.format_exc()))

# Set to True to display various useful messages when debugging your app
debug = True

def run(context):
    my_addin.run_app()

def stop(context):
    my_addin.stop_app()

