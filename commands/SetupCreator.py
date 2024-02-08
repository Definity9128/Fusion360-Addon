import adsk.core
import adsk.fusion
import adsk.cam

# Import the entire apper package
from ..apper import apper
from .. import config

class SetupCreator(apper.Fusion360CommandBase):
    # ... [Other methods] ...

    def on_execute(self, command, inputs, args, input_values):
        app = adsk.core.Application.get()
        ui = app.userInterface

        # Access the CAM environment
        cam = adsk.cam.CAM.cast(app.activeProduct)
        if not cam:
            ui.messageBox("CAM environment is not available", "No CAM")
            return

        # Get the selected body
        selection = inputs.itemById('body_selection')
        selected_body = None
        if selection.selectionCount > 0:
            selected_entity = selection.selection(0).entity
            if isinstance(selected_entity, adsk.fusion.BRepBody):
                selected_body = selected_entity

        if selected_body:
            try:
                setups = cam.setups
                setupInput = setups.createInput(adsk.cam.OperationTypes.MillingOperation)
                setupInput.models = [selected_body]

                # Set additional setup properties here

                newSetup = setups.add(setupInput)
                ui.messageBox('Setup created successfully for the selected body.')
            except Exception as e:
                ui.messageBox('Failed to create setup:\n{}'.format(str(e)))
        else:
            ui.messageBox("No body selected.")

    def on_create(self, command, inputs):
        body_selection_input = inputs.addSelectionInput('body_selection', 'Select Body', 'Select a body for setup creation')
        body_selection_input.setSelectionLimits(1, 1)
        body_selection_input.addSelectionFilter('SolidBodies')

        print("Attempting to Generate")
