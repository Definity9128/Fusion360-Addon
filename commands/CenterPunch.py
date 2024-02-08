import adsk.core, adsk.fusion, adsk.cam, traceback
from ..apper import apper
 
class CenterPunch(apper.Fusion360CommandBase):
 
    def on_create(self, command, inputs):
        # Add a selection input for choosing the face
        face_selection = inputs.addSelectionInput('face_selection', 'Select Face', 'Select a face to place the center mark')
        face_selection.addSelectionFilter('PlanarFaces')
        face_selection.setSelectionLimits(1, 1)
 
        # Add a selection input for choosing the body
        body_selection = inputs.addSelectionInput('body_selection', 'Select Body', 'Select a body to cut into')
        body_selection.addSelectionFilter('SolidBodies')
        body_selection.setSelectionLimits(1, 1)
 
    def calculate_center_of_mass(self, selected_face):
        parent_component = selected_face.body
        return parent_component.physicalProperties.centerOfMass if parent_component else None
 
    def create_center_mark_on_face(self, selected_face, target_body):
        app = adsk.core.Application.cast(adsk.core.Application.get())
        design = app.activeProduct
        root_comp = design.rootComponent
        center_point = self.calculate_center_of_mass(selected_face)
 
        if center_point:
            construction_plane_input = root_comp.constructionPlanes.createInput()
            construction_plane_input.setByPlane(adsk.core.Plane.create(center_point, selected_face.geometry.normal))
            construction_plane = root_comp.constructionPlanes.add(construction_plane_input)
            sketch = root_comp.sketches.add(construction_plane)
            radius_in_cm = 1.5 * 2.54 / 2
            offset_distance = 2.31
            adjusted_center_point = adsk.core.Point3D.create(center_point.x, center_point.y, center_point.z + offset_distance)
            circle = sketch.sketchCurves.sketchCircles.addByCenterRadius(adjusted_center_point, radius_in_cm)
            circle.isConstruction = False
            sketch.name = "CenterPunchSketch"
            self.create_circle_array(sketch, adjusted_center_point, 96 * 2.54, 4, 4)
            self.cut_holes(sketch, target_body)
 
    def create_circle_array(self, sketch, center_point, distance, rows, columns):
        for i in range(-rows // 2, rows // 2 + 1):
            for j in range(-columns // 2, columns // 2 + 1):
                x_offset = i * distance
                y_offset = j * distance
                new_center_point = adsk.core.Point3D.create(center_point.x + x_offset, center_point.y + y_offset, center_point.z)
                sketch.sketchCurves.sketchCircles.addByCenterRadius(new_center_point, 1.5 * 2.54 / 2)
 
    def cut_holes(self, sketch, target_body):
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = app.activeProduct
        rootComp = design.rootComponent
        # Define the depth of the hole in both directions in centimeters
        depth_up = 1000*2.54  # +10 cm
        depth_down = -1000*2.54  # -10 cm
 
        for prof in sketch.profiles:
            try:
                if prof.areaProperties().area > 0:
                    # Extrude up (+10cm)
                    ext_input_up = rootComp.features.extrudeFeatures.createInput(prof, adsk.fusion.FeatureOperations.CutFeatureOperation)
                    ext_input_up.participantBodies = [target_body]
                    distanceExtentUp = adsk.fusion.DistanceExtentDefinition.create(adsk.core.ValueInput.createByReal(depth_up))
                    ext_input_up.setOneSideExtent(distanceExtentUp, adsk.fusion.ExtentDirections.PositiveExtentDirection)
                    rootComp.features.extrudeFeatures.add(ext_input_up)
 
                    # Extrude down (-10cm)
                    ext_input_down = rootComp.features.extrudeFeatures.createInput(prof, adsk.fusion.FeatureOperations.CutFeatureOperation)
                    ext_input_down.participantBodies = [target_body]
                    distanceExtentDown = adsk.fusion.DistanceExtentDefinition.create(adsk.core.ValueInput.createByReal(abs(depth_down)))
                    ext_input_down.setOneSideExtent(distanceExtentDown, adsk.fusion.ExtentDirections.NegativeExtentDirection)
                    rootComp.features.extrudeFeatures.add(ext_input_down)
            except Exception as e:
                # Print the error message to the Python Console
                print('Failed to create hole for one of the profiles:\n{}'.format(traceback.format_exc()))
 
    def on_destroy(self, command, inputs, reason, input_values):
        if inputs.itemById('face_selection').selectionCount > 0 and inputs.itemById('body_selection').selectionCount > 0:
            selected_face = inputs.itemById('face_selection').selection(0).entity
            target_body = inputs.itemById('body_selection').selection(0).entity
            self.create_center_mark_on_face(selected_face, target_body)
 
    def on_execute(self, command, inputs, args, input_values):
        pass