import adsk.core
import adsk.fusion
import adsk.cam
import math
import copy

# Import the entire apper package
from ..apper import apper
from .. import config

from .. import helper_functions as helper

# Fusion constants
PLANAR_SURFACE = 0

# Class for a Fusion 360 Command
# Place your program logic here
# Delete the line that says "pass" for any method you want to use
class GenerateGridlines(apper.Fusion360CommandBase):
    

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


    # Run when the user presses OK
    # This is typically where your main program logic would go
    def on_execute(self, command, inputs, args, input_values):
        print("Executing")
        ao = apper.AppObjects()
        app = adsk.core.Application.get()
        ui  = app.userInterface
        des = adsk.fusion.Design.cast(app.activeProduct)
        root = adsk.fusion.Component.cast(des.rootComponent)

        # Selected face
        face_inputs = input_values.get('face_input', None)
        face = face_inputs[0]

        # Edge offsets
        offset1 = input_values['offset_input']
        offset2 = input_values['offset2_input']

        # Offset2 edges
        offset2_selections = input_values.get('offset2_edge_input', None)
        

        # Top edge
        top_edge_selections = input_values.get('top_edge_input', None)
        top_edge = top_edge_selections[0]

        # grid spacing
        grid_spacing = input_values['grid_spacing_input']

        # Create a sketch.
        sk = root.sketches.addWithoutEdges(face)
        sk.name = "Vertical Grid"
        sk_h = root.sketches.addWithoutEdges(face)
        sk_h.name = "Horizontal Grid"

        innerRectangles = []

        for loop in face.loops:
            
            if loop.isOuter:
                if loop.coEdges.count!=4:
                    ao.ui.messageBox('Sorry, this function only works with rectangles.')
                    return

                points = []
                normVectors = []
                offsets = []
                top_edge_loc = None
                
                for coEdge in loop.coEdges:
                    (start, end) = helper.getCoEdgeEnds(coEdge)
                    points.append(start)

                    offset = offset2 if coEdge.edge in offset2_selections else offset1
                    offsets.append(offset)

                    vector = start.vectorTo(end)
                    vector.normalize()
                    normVectors.append(vector)

                    if coEdge.edge == top_edge:

                        top_edge_loc = len(points)-1

                if top_edge==None:
                    ui.messageBox("Selected top edge wasn't found in face.")
                    return

                # Create offset rectangle
               
                #returnPts = createOffsetRectangle(points, offsets, normVectors, offsetInwards): 
                outerRectangle = helper.createOffsetRectangle(points, offsets, normVectors, True)

            # Create outwards offsets around inner loops
            else:
                if loop.coEdges.count!=4:
                    print("skipping inner loop with not4 edges")
                    continue

                points = []
                normVectors = []
                offsets = []

                for coEdge in loop.coEdges:
                    (start, end) = helper.getCoEdgeEnds(coEdge)
                    points.append(start)

                    offset = offset2 if coEdge.edge in offset2_selections else offset1
                    offsets.append(offset)

                    vector = start.vectorTo(end)
                    vector.normalize()
                    normVectors.append(vector)

                # Create offset rectangle
                innerRectangles.append(helper.createOffsetRectangle(points, offsets, normVectors, False))
                    
        # Draw some geometry.
        #helper.sketchShapeByPoints(sk, outerRectangle)
        innerRectangleSketchLines = []
        for rectangle in innerRectangles:
            innerRectangleSketchLines.append(helper.sketchShapeByPoints(sk, rectangle))
        for rectangle in innerRectangleSketchLines:
            for sketchLine in rectangle:
                sketchLine.isConstruction = True

        # Create vertical lines
        # top_edge_loc is top-right corner
        OR = outerRectangle
        rt = OR[top_edge_loc]
        rb = OR[(len(OR)+top_edge_loc-1)%len(OR)]
        lt = OR[(top_edge_loc+1)%len(OR)]
        lb = OR[(top_edge_loc+2)%len(OR)]

        v_top = lt.vectorTo(rt)
        v_top.normalize()
        v_first = v_top.copy()
        v_top.scaleBy(grid_spacing)
        p_top = lt.copy()
        p_low = lb.copy()

        # Create vertical grid 
        # Create object collection
        vertGridlines = adsk.core.ObjectCollection.create()
        (firstOffset,numVert) = helper.getGridOffset(lt.distanceTo(rt),grid_spacing)
        v_first.scaleBy(firstOffset)
        print("Vertical grid")
        print(grid_spacing)
        print(numVert)
        print(firstOffset)
        for i in range(0,numVert):
            vertGridlines.add(helper.sketchShapeByPoints(sk, [p_top,p_low]))
            nextSpacing = v_top if i!=0 else v_first
            p_top.translateBy(nextSpacing)
            p_low.translateBy(nextSpacing)
        helper.sketchShapeByPoints(sk, [rt,rb])  
            
        # Create horzontal grid
        horGridlines = adsk.core.ObjectCollection.create()
        p_left = lt.copy()
        p_right = rt.copy()
        v_first = lt.vectorTo(lb)
        v_first.normalize()
        v_down = v_first.copy()
        v_down.scaleBy(grid_spacing)
        (firstOffset,numHor) = helper.getGridOffset(lt.distanceTo(lb),grid_spacing)
        v_first.scaleBy(firstOffset)
        print("Horizontal grid")
        print(grid_spacing)
        print(numHor)
        print(firstOffset)
        for i in range(0,numHor):
            horGridlines.add(helper.sketchShapeByPoints(sk_h, [p_left,p_right]))
            nextSpacing = v_down if i!=0 else v_first
            p_left.translateBy(nextSpacing)
            p_right.translateBy(nextSpacing)
        helper.sketchShapeByPoints(sk_h, [lb,rb])  

        #split all grid lines using inner rectangles
        for rectangle in innerRectangleSketchLines:
            for sketchLine in rectangle:
                # cut all intersecting sketchlines at the point of intersection
                ####### use grid lines as arg for intersections()
                (areIntersections, intersectingCurves, intersectionPoints) = sketchLine.intersections(vertGridlines)
                if areIntersections:
                    for i in range(0,len(intersectingCurves)):
                        splitLines = intersectingCurves.item(i).split(intersectionPoints[i])
                        vertGridlines.add(splitLines.item(1))
                (areIntersections, intersectingCurves, intersectionPoints) = sketchLine.intersections(horGridlines)
                if areIntersections:
                    for i in range(0,len(intersectingCurves)):
                        splitLines = intersectingCurves.item(i).split(intersectionPoints[i])
                        horGridlines.add(splitLines.item(1))
                #Delete line when finished
                #sketchLine.deleteMe()

        
    # Run when the user selects your command icon from the Fusion 360 UI
    # Typically used to create and display a command dialog box
    # The following is a basic sample of a dialog UI

    def on_create(self, command, inputs):

        ao = apper.AppObjects()

        print("MAKESKETCH")

        # Get teh user's current units
        default_units = ao.units_manager.defaultLengthUnits

        # Create a value input.  This will respect units and user defined equation input.
        inputs.addValueInput('grid_spacing_input', 'Grid Spacing', default_units, adsk.core.ValueInput.createByString('6.0 in'))
        inputs.addValueInput('offset_input', 'Standard Offset', default_units, adsk.core.ValueInput.createByString('2.375 in'))
        inputs.addValueInput('offset2_input', 'Secondary Offset', default_units, adsk.core.ValueInput.createByString('2.375 in'))

        # [parameter_id, label, tooltip_label, selection_filter, selection_limit]
        helper.addSelectionInput(inputs, 'face_input', 'Face', 'Select a face', 'Faces', (1,1))
        helper.addSelectionInput(inputs, 'offset2_edge_input', 'Secondary Offset Edges', 'Select offset2 edges', 'Edges', (0,0))
        helper.addSelectionInput(inputs, 'top_edge_input', 'Top edge', 'Select top edge', 'Edges', (1,1))


