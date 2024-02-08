def convertMMToInches(valueMM):
    return 0.0393701*float(valueMM)

def printSetupParameters(parameters):
    for p in parameters:
        print(p.name, p.expression)
    # job_stockOffsetSides
    # job_stockOffsetTop
    # stockXLow
    # stockXHigh
    # stockYLow
    # stockYHigh
    # stockZLow
    # stockZHigh

def listAsArray(list):
    arrList = []
    for item in list:
        arrList.append(item.asArray())
    return arrList


def sketchShapeByPoints(sk, points):
    if len(points)==1:
        # Add a single point
        return
    if len(points)==2:
        return sk.sketchCurves.sketchLines.addByTwoPoints(sk.modelToSketchSpace(points[0]),sk.modelToSketchSpace(points[1]))

    newLines = [] 
    for p1 in range(0,len(points)):
        p2 = p1+1 if p1<(len(points)-1) else 0
        newLines.append(sk.sketchCurves.sketchLines.addByTwoPoints(sk.modelToSketchSpace(points[p1]),sk.modelToSketchSpace(points[p2])))
        #sk.sketchCurves.sketchLines.addByTwoPoints(sk.modelToSketchSpace(points[p1]),sk.modelToSketchSpace(points[p2]))
    return newLines

    
def addSelectionInput(inputs, parameter_id, label, tooltip_label, selection_filter, selection_limit):
    newInput = inputs.addSelectionInput(parameter_id, label, tooltip_label)
    if selection_filter:
        newInput.addSelectionFilter(selection_filter)
    if selection_limit:
        try:
            newInput.setSelectionLimits(selection_limit[0],selection_limit[1])
        except:
            newInput.setSelectionLimits(selection_limit[0])

def createOffsetRectangle(points, offsets, normVectors, offsetInwards):
    offsetPts = []
    for p1 in range(0,len(normVectors)):
        p2 = p1-1 if p1>=1 else len(normVectors)-1

        dir1 = 1 if offsetInwards else -1
        dir2 = -1 if offsetInwards else 1

        v1 = normVectors[p1].copy()
        v1.scaleBy(dir1*offsets[p2])
        
        v2 = normVectors[p2].copy()
        v2.scaleBy(dir2*offsets[p1])

        offsetPt = points[p1].copy()
        offsetPt.translateBy(v1)
        offsetPt.translateBy(v2)
        offsetPts.append(offsetPt)
    return(offsetPts)

def getCoEdgeEnds(coEdge):
    start = coEdge.edge.startVertex.geometry if not coEdge.isOpposedToEdge else coEdge.edge.endVertex.geometry
    end = coEdge.edge.startVertex.geometry if coEdge.isOpposedToEdge else coEdge.edge.endVertex.geometry
    return (start, end)

def getGridOffset(length, grid_spacing):
    numLines = int(float(length)/float(grid_spacing))

    rem = float(length)%float(grid_spacing)
    #Maximum error will be +/- 0.25*grid_spacing
    if rem>=(0.5*grid_spacing):
        print("split large offset, add 1")
        return ((grid_spacing+rem)/2, numLines+1)
    else:
        print("split small offset")
        return (grid_spacing + rem/2, numLines)