import adsk.core
import adsk.fusion
import adsk.cam
import os
# Import the entire apper package
from ..apper import apper
from .. import config

# Import project config
# This file can be edited to change defaults
from .. import project_config as proj

from .. import helper_functions as h

# Class for a Fusion 360 Command
# Place your program logic here
# Delete the line that says "pass" for any method you want to use
class PostProcess(apper.Fusion360CommandBase):
    
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
        self.post(
            input_values['job_id'], 
            input_values['project'], 
            input_values['post_file'], 
            input_values['toolpath_directory'], 
            input_values['version'],
            input_values['openFiles'],
            input_values['billet_width']
        )
        
    # Run when the user selects your command icon from the Fusion 360 UI
    # Typically used to create and display a command dialog box
    # The following is a basic sample of a dialog UI
    def on_create(self, command, inputs):
        # Get the user's current units
        ao = apper.AppObjects()
        default_units = ao.units_manager.defaultLengthUnits
        
        # Create dialogue for user inputs
        inputs.addStringValueInput('job_id', 'Job ID')  
        self.addProjectSelectionList(inputs)
        inputs.addStringValueInput('post_file', 'Post File', proj.POST_NAME)
        inputs.addStringValueInput('toolpath_directory', 'Toolpath Directory', proj.TOOLPATH_DIRECTORY)
        inputs.addStringValueInput('version', 'Version')
        inputs.addBoolValueInput('openFiles', 'Open files on completion', True, "", proj.OPEN_FILES)
        inputs.addValueInput('billet_width', 'Billet Width', default_units, adsk.core.ValueInput.createByString(proj.BILLET_WIDTH))

    # Create dropdown selection list for project folders within toolpath directory
    # To add a project, edit project_config.py
    def addProjectSelectionList(self, inputs):
        drop_style = adsk.core.DropDownStyles.TextListDropDownStyle
        drop_down_input = inputs.addDropDownCommandInput('project', 'Project', drop_style)
        for projectName in proj.PROJECT_LIST:
            isSelected = projectName==proj.PROJECT_LIST[0]
            drop_down_input.listItems.add(projectName, isSelected)

    # Post process all setups in the CAM product using configuration constants
    # Save to toolpath folder inside directory <Project>/<JobID>
    def post(self, job_id, project, post_file, toolpath_directory, version, open_files, billet_width):
        app = adsk.core.Application.get()
        ui  = app.userInterface
        
        if not job_id:
            ui.messageBox('Job ID is required.')
            return
        if not project:
            ui.messageBox('Project name is required.')
            return
        if not post_file:
            ui.messageBox('Post file name is required.')
            return
        if not toolpath_directory:
            ui.messageBox('Toolpath directory is required.')
            return

        # Get the CAM product.
        doc = app.activeDocument
        products = doc.products
        camProduct = products.itemByProductType('CAMProductType')
        # Check if the document has a CAMProductType. It will not if there are no CAM operations in it.
        if camProduct == None:
            ui.messageBox('There are no CAM operations in the active document')
            return
        # Cast the CAM product to a CAM object (a subtype of product).
        cam = adsk.cam.CAM.cast(camProduct)

        # Post configurations
        outputFolder = toolpath_directory + '/' + project + '/' + job_id
        #postConfig = cam.genericPostFolder + '/' + post_file
        postConfig = proj.POST_LOCATION + '/' + post_file
        
        units = adsk.cam.PostOutputUnitOptions.DocumentUnitsOutput

        # Post-process all toolpaths
        setups = cam.setups
        setupCount = 0
        for setup in setups:
            setupCount += 1
            par = setup.parameters
            # Uncomment to list all setup parameters
            # h.printSetupParameters(par)

            # Generate program information headers
            offsetSide = par.itemByName('job_stockOffsetSides').expression
            offsetTop = par.itemByName('job_stockOffsetTop').expression
            sizeX = h.convertMMToInches(par.itemByName('stockXHigh').expression)-h.convertMMToInches(par.itemByName('stockXLow').expression)
            sizeY = h.convertMMToInches(par.itemByName('stockYHigh').expression)-h.convertMMToInches(par.itemByName('stockYLow').expression)
            sizeZ = h.convertMMToInches(par.itemByName('stockZHigh').expression)-h.convertMMToInches(par.itemByName('stockZLow').expression)
            billetWidthInch = h.convertMMToInches(billet_width*10)
            numBillets = sizeX/billetWidthInch if billetWidthInch!=0 else 0

            # Specify the program name.
            """setupName = par.itemByName('job_programName').expression
            if setupName=="\'\'":
                setupName = setup.name"""
            programName = f'{job_id}_cut{setupCount}'

            # Append optional version code
            if version:
                programName += f'_{version}'

            # Create the postInput object.
            postInput = adsk.cam.PostProcessInput.create(programName, postConfig, outputFolder, units)

            # Open the resulting NC file in the editor for viewing
            postInput.isOpenInEditor = open_files

            # Add comment to NC file header
            postInput.programComment = f'STOCK SIZE: X={sizeX:.2f} Y={sizeY:.2f} Z={sizeZ:.2f}, Side offset={offsetSide}, Top offset={offsetTop}, {billetWidthInch:.2f}in Billets={numBillets:.2f}'

            # Post process setup
            cam.postProcess(setup, postInput)
        app = adsk.core.Application.get()
        ui = app.userInterface
        doc = app.activeDocument
        products = doc.products
        product = products.itemByProductType('CAMProductType')

        # check if the document has a CAMProductType.  It will not if there are no CAM operations in it.
        if not product:
            ui.messageBox('There are no CAM operations in the active document.  This script requires the active document to contain at least one CAM operation.',
                            'No CAM Operations Exist',
                            adsk.core.MessageBoxButtonTypes.OKButtonType,
                            adsk.core.MessageBoxIconTypes.CriticalIconType)
            return

        cam = adsk.cam.CAM.cast(product)

        # specify the output folder and format for the setup sheets
        sheetFormat = adsk.cam.SetupSheetFormats.HTMLFormat
        #sheetFormat = adsk.cam.SetupSheetFormats.ExcelFormat (not currently supported on Mac)

        # prompt the user with an option to view the resulting setup sheets.
        viewResults = ui.messageBox('View setup sheets when done?', 'Generate Setup Sheets',
                                    adsk.core.MessageBoxButtonTypes.YesNoButtonType,
                                    adsk.core.MessageBoxIconTypes.QuestionIconType)
        if viewResults == adsk.core.DialogResults.DialogNo:
            viewResult = False
        else:
            viewResult = True

        # set the value of scenario to 1, 2 or 3 to generate setup sheets for all, for the first setup, or for the first operation of the first setup.
        scenario = 1
        if scenario == 1:
            ui.messageBox('Setup sheets for all operations will be generated.')
            cam.generateAllSetupSheets(sheetFormat, outputFolder, viewResult)
        elif scenario == 2:
            ui.messageBox('Setup sheets for operations in the first setup will be generated.')
            setup = cam.setups.item(0)
            cam.generateSetupSheet(setup, sheetFormat, outputFolder, viewResult)
        elif scenario == 3:
            ui.messageBox('A setup sheet for the first operation in the first setup will be generated.')
            setup = cam.setups.item(0)
            operations = setup.allOperations
            operation = operations.item(0)
            if operation.hasToolpath:
                cam.generateSetupSheet(operation, sheetFormat, outputFolder, viewResult)
            else:
                ui.messageBox('This operation has no toolpath.  A valid toolpath must exist in order for a setup sheet to be generated.')
                return

        ui.messageBox('Setup Sheets have been generated in:\n' + outputFolder)

        # open the output folder in Finder on Mac or in Explorer on Windows
        #if (os.name == 'posix'):
        #    os.system('open "%s"' % outputFolder)
        #elif (os.name == 'nt'):
        #    os.startfile(outputFolder)

        # Prompt user with an option to switch to the CAM workspace if it's not already active
        if ui.activeWorkspace.name != 'CAM':
            activateCAMWorkspace = ui.messageBox('Activate the CAM Workspace?','CAM Workspace Activate',
                                                 adsk.core.MessageBoxButtonTypes.YesNoButtonType,
                                                 adsk.core.MessageBoxIconTypes.QuestionIconType)

            if activateCAMWorkspace == adsk.core.DialogResults.DialogYes:
                workspaces = ui.workspaces
                camWorkspace = workspaces.itemById("CAMEnvironment")
                camWorkspace.activate()


        if not open_files:
            ui.messageBox(f'Toolpaths saved to {project}/{job_id}')
        