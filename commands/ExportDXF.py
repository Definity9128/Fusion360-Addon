import adsk.core
import adsk.fusion

# Import the entire apper package
from ..apper import apper
#from .. import config

# Import project config
# This file can be edited to change defaults
from .. import project_config as proj

# ExportDXF take a face as an input and exports its contours as a DXF
class ExportDXF(apper.Fusion360CommandBase):
    
    # Run whenever a user makes any change to a value or selection in the addin UI
    # Commands in here will be run through the Fusion processor and changes will be reflected in  Fusion graphics area
    def on_preview(self, command, inputs, args, input_values):
        pass

    # Run after the command is finished.
    # Can be used to launch another command automatically or do other clean up.
    def on_destroy(self, command, inputs, reason, input_values):
        pass

    # Run when any input is changed.
    # Can be used to check a value and then update the add-in UI accordingly
    def on_input_changed(self, command, inputs, changed_input, input_values):
        pass

    # Run when the user selects your command icon from the Fusion 360 UI
    # Typically used to create and display a command dialog box
    # The following is a basic sample of a dialog UI
    def on_create(self, command, inputs):
        # Get teh user's current units
        ao = apper.AppObjects()
        default_units = ao.units_manager.defaultLengthUnits
        
        # Create dialogue for user inputs
        inputs.addStringValueInput('filename', 'Filename')
        inputs.addStringValueInput('directory', 'Directory', proj.DXF_OUTPUT_DIRECTORY)
        inputs.addSelectionInput('face_input', 'Face', 'Select Something').addSelectionFilter('Faces')

    # Run when the user presses OK
    # This is typically where your main program logic would go
    def on_execute(self, command, inputs, args, input_values):
        app = adsk.core.Application.get()
        ui  = app.userInterface
        design = app.activeDocument.products.itemByProductType('DesignProductType')
        if design == None:
            ui.messageBox("Unable to find Design product")
            return
        root = adsk.fusion.Component.cast(design.rootComponent)

        # DXf Filename
        filename_input = input_values['filename'], 
        filename = filename_input[0]
        directory_input = input_values['directory'], 
        directory = directory_input[0]
        if filename == '':
            ui.messageBox("Filename is required")
            return
        else:
            if directory == '':
                ui.messageBox("Directory is required")
                return
        filepath = f'{directory}/{filename}.dxf'    
        # Selected face
        face_inputs = input_values.get('face_input', None)
        face = face_inputs[0]
        sk = root.sketches.add(face)

        #Generate DXF
        result = sk.saveAsDXF(filepath)
        if result:
            ui.messageBox(f'DXF saved as {filepath}')
        else:
            ui.messageBox(f'Unable to save as {filepath}')
        #Delete sketch when finished
        sk.deleteMe()
        
    