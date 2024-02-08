import adsk.core, adsk.fusion, adsk.cam, traceback
from ..apper import apper

class AutoProjectEdges(apper.Fusion360CommandBase):

    def on_create(self, command, inputs):
        # Add a selection input for choosing the plane or face to project onto
        plane_selection = inputs.addSelectionInput('plane_selection', 'Select Plane/Face', 'Select a plane or face for projection')
        plane_selection.addSelectionFilter('PlanarFaces')
        plane_selection.addSelectionFilter('ConstructionPlanes')
        plane_selection.setSelectionLimits(1, 1)

    def project_onto_selected_plane(self, selectedEntity):
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = app.activeProduct
        rootComp = design.rootComponent
        sketches = rootComp.sketches
        sketch = sketches.add(selectedEntity)

        # Project all bodies in the design onto the sketch
        for body in rootComp.bRepBodies:
            sketch.projectCutEdges(body)

    def on_destroy(self, command, inputs, reason, input_values):
        if inputs.itemById('plane_selection').selectionCount > 0:
            selected_plane_or_face = inputs.itemById('plane_selection').selection(0).entity
            self.project_onto_selected_plane(selected_plane_or_face)
            adsk.core.Application.get().userInterface.messageBox('Projection completed successfully.')

    def on_execute(self, command, inputs, args, input_values):
        # The projection logic is handled in the on_destroy to ensure it executes after the selection.
        pass
