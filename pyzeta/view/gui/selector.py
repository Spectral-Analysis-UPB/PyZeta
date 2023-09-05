"""
Module `pyzeta.view.gui.selector` from the `PyZeta` project. It provides
plotting and selection utilities for resonances of zeta functions.

Authors:\n
- Philipp Schuette\n
- Sebastian Albrecht\n
"""

# To view the dynamic bokeh document, run
#  $ python -m bokeh serve selector.py --dev --show
# in the console

import os
from typing import Dict, List, Optional

import numpy as np
from bokeh.events import MenuItemClick
from bokeh.layouts import column, row
from bokeh.model import Model
from bokeh.models import (
    BoxSelectTool,
    Button,
    ColorBar,
    ColumnDataSource,
    Div,
    Dropdown,
    HoverTool,
    PanTool,
    PrintfTickFormatter,
    ResetTool,
    Select,
    TapTool,
    TextInput,
    WheelZoomTool,
    ZoomInTool,
    ZoomOutTool,
)
from bokeh.plotting import curdoc, figure
from bokeh.transform import factor_mark, linear_cmap
from numpy.typing import NDArray
from pyzeta.handler import fromFile, toFile

import pyzeta.view.gui.constants as constants
from pyzeta.framework.pyzeta_logging.loggable import Loggable


class ResonanceSelector(Loggable):
    "Class providing plotting utilities for resonances of zeta function."

    __slots__ = ("source", "layout", "handlerData")

    def __init__(self) -> None:
        """
        Create a new instance of ResonanceSelector class.

        This sets up a static bokeh document without dynamic functionality.
        To use all the functionality of the selector, call the method
        `ResonanceSelector.plot()` on the newly initialised instance.
        The correspondig code should be placed inside a python script. Run the
        script on a bokeh server from the console. This will start the dynamic
        bokeh application in a preinstalled browser.
        """
        # set up Bokeh figure
        fig = figure(
            min_width=300,
            width_policy="max",
            background_fill_color="#fafafa",
            x_axis_label="Re(z)",
            y_axis_label="Im(z)",
        )

        # set up Bokeh widgets
        cwdText = TextInput(
            value=os.getcwd(),
            height=30,
            height_policy="fixed",
            max_width=220,
            margin=(5, 0, 5, 5),
            name="cwdText",
        )
        loadText = TextInput(
            placeholder="res_data",
            height=30,
            height_policy="fixed",
            max_width=240,
            margin=(5, 0, 5, 5),
            name="loadText",
        )
        saveText = TextInput(
            placeholder="select_data",
            height=30,
            height_policy="fixed",
            max_width=240,
            margin=(5, 0, 5, 5),
            name="saveText",
        )

        cwdButton = Button(
            label="change cwd",
            button_type="primary",
            height=31,
            height_policy="fixed",
            width=85,
            width_policy="fixed",
            margin=(5, 5, 5, -5),
            name="cwdButton",
        )
        loadButton = Dropdown(
            label="Load/Clear data",
            menu=[
                ("Load (Overwrite current plot)", "overwrite"),
                ("Load (Add data to current plot)", "add"),
                ("Clear data by filename/number", "clearSpecific"),
                ("Clear all data", "clear"),
            ],
            button_type="primary",
            name="loadButton",
        )
        saveButton = Button(
            label="Save data", button_type="primary", name="saveButton"
        )

        loadTypeSelect = Select(
            value=".npz",
            options=[".npz", ".txt"],
            height=30,
            height_policy="fixed",
            width=65,
            width_policy="fixed",
            margin=(5, 5, 5, -5),
            name="loadTypeSelect",
        )
        saveTypeSelect = Select(
            value=".npz",
            options=[".npz", ".txt"],
            height=30,
            height_policy="fixed",
            width=65,
            width_policy="fixed",
            margin=(5, 5, 5, -5),
            name="saveTypeSelect",
        )
        colorCodeSelect = Select(
            title="Color Encoding",
            value="absErr",
            options=[
                ("order", "Zero Order"),
                ("absErr", "Rootfinder Error"),
                ("absPropErr", "Propagated Error"),
                ("idx", "Ordering of Data Points"),
                ("", "Nothing"),
            ],
            max_width=300,
            name="colorCodeSelect",
        )
        colorMapSelect = Select(
            title="Color Map",
            value="Plasma",
            options=list(constants.CMAPS.keys()),
            max_width=300,
            name="colorMapSelect",
        )

        headingDiv = Div(
            text=("<h1>PyZeta Resonance Selector</h1>"),
            sizing_mode="stretch_width",
            name="headingDiv",
        )
        loadTitle = Div(text="Load/Clear resonance data:", name="loadTitle")
        saveTitle = Div(text="Save resonance data:", name="saveTitle")
        feedbackDiv = Div(
            text=" ", height=180, height_policy="fixed", name="feedbackDiv"
        )

        # set up layout
        cwdWidgets = row(cwdText, cwdButton)
        loadWidgets = column(
            [loadTitle, row([loadText, loadTypeSelect]), loadButton]
        )
        saveWidgets = column(
            [saveTitle, row([saveText, saveTypeSelect]), saveButton]
        )
        plotProperties = column([colorCodeSelect, colorMapSelect])
        widgets = column(
            [cwdWidgets, loadWidgets, saveWidgets, feedbackDiv, plotProperties]
        )

        self.layout = column(
            [
                headingDiv,
                row([widgets, fig], width_policy="max", height_policy="max"),
            ],
            width_policy="max",
            height_policy="max",
        )

        # initialize a ColumnDataSource object to store all data for plotting
        self.source = ColumnDataSource()
        # initialize a dictinary to store metadata from loaded files
        self.handlerData = {}

    def select(self, name: str) -> Model:
        """
        Query the underlying bokeh document for an object by `name`.

        :param name: name of the bokeh object
        :return: the unique bokeh object with the specified `name` or None if
            the object could not be identified
        """
        try:
            return self.layout.select_one({"name": name})
        except ValueError as err:
            self.logger.warning(
                "%s, assume last element was querried for", str(err)
            )
            return self.layout.select({"name": name})[-1]

    def updateFigure(self) -> None:
        "Update figure with scatter plot."
        # clean up old scatter plot
        previousScat = self.select("scat")
        if previousScat is not None:
            selectedIndices = previousScat.data_source.selected.indices.copy()
        else:
            selectedIndices = []

        # remove old figure
        del self.layout.children[1].children[1]

        # set up new Bokeh figure tools
        boxSelect = BoxSelectTool(mode="append", select_every_mousemove=True)
        tapSelect = TapTool(mode="subtract")
        reset = ResetTool()
        pan = PanTool()
        wheelZoom = WheelZoomTool()
        zoomIn = ZoomInTool()
        zoomOut = ZoomOutTool()
        hover = HoverTool(
            tooltips=[
                ("Resonance", r"@resR{%.4g}@resI{%+.4g}j"),
                ("Zero Order", "@order"),
                ("Error", "@errR{%.4g}@errI{%+.4g}j"),
                ("Propagated Error", "@propErrR{%.4g}@propErrI{%+.4g}j"),
            ],
            formatters={
                "@resR": "printf",
                "@resI": "printf",
                "@errR": "printf",
                "@errI": "printf",
                "@propErrR": "printf",
                "@propErrI": "printf",
            },
            point_policy="snap_to_data",
            toggleable=False,
        )

        tools = [
            boxSelect,
            tapSelect,
            reset,
            pan,
            wheelZoom,
            zoomIn,
            zoomOut,
            hover,
        ]

        # set up new Bokeh figure
        fig = figure(
            min_width=300,
            width_policy="max",
            tools=tools,
            active_drag=pan,
            active_scroll=wheelZoom,
            toolbar_location="above",
            background_fill_color="#fafafa",
            x_axis_label="Re(z)",
            y_axis_label="Im(z)",
            name="fig",
        )
        fig.toolbar.autohide = False
        fig.toolbar.logo = None
        fig.x_range.range_padding = 0.5
        fig.y_range.range_padding = 0.5
        if len(self.handlerData) == 0:
            fig.title.text = "PyZeta Project"
        else:
            fig.title.text = (
                "Resonances for " + self.handlerData["surfaceName"]
            )

        # create new color bar
        colorCode = self.select("colorCodeSelect").value
        palette = constants.CMAPS[self.select("colorMapSelect").value]
        drawColorBar = True
        if len(colorCode) == 0:
            colorCode = "idx"
            palette = palette[128:129]
            drawColorBar = False

        colorMapper = linear_cmap(
            colorCode,
            palette,
            low=0.99 * np.nanmin(self.source.data[colorCode]),
            high=1.01 * np.nanmax(self.source.data[colorCode]),
            nan_color="grey",
        )

        colorBar = ColorBar(
            color_mapper=colorMapper["transform"],
            location="center_right",
            margin=5,
            padding=5,
            visible=drawColorBar,
            name="colorBar",
        )
        tickFormat = (
            "%-7.1e" if colorCode in ["absErr", "absPropErr"] else "%-7u"
        )
        colorBar.formatter = PrintfTickFormatter(format=tickFormat)
        colorBar.label_standoff = 13
        fig.add_layout(colorBar, "center")

        # create new scatter plot
        fileNames = np.unique(self.source.data["file"])
        markerMapper = factor_mark("file", constants.MARKERS, fileNames)
        scat = fig.scatter(
            "resR",
            "resI",
            source=self.source,
            size=15.0,
            color=colorMapper,
            marker=markerMapper,
            alpha=0.6,
            selection_alpha=0.9,
            selection_line_width=5.0,
            nonselection_alpha=0.3,
            legend_group="file",
            name="scat",
        )
        scat.data_source.selected.indices = selectedIndices
        fig.legend.location = "top_left"

        self.layout.children[1].children.append(fig)

    def updateButtonStyles(
        self, success: Optional[str] = None, warning: Optional[str] = None
    ) -> None:
        """
        Update which button is displayed in style "success" or style "warning.

        The remainiung buttons are set to style "primary".

        :param success: name of the successfull button, defaults to None
        :param warning: name of the warning button, defaults to None
        """
        for buttonName in ["cwdButton", "loadButton", "saveButton"]:
            self.select(buttonName).button_type = "primary"

        if success is not None:
            self.select(success).button_type = "success"
        if warning is not None:
            self.select(warning).button_type = "warning"

    def loadData(self, overwriteData: bool = False) -> None:
        """
        Load data from file.

        :param overwriteData: whether an existing file with the given
            `filename` should be overwritten, defaults to False
        """
        # retrieve fileName
        fileName = (
            self.select("loadText").value.strip()
            or self.select("loadText").placeholder
        )
        filetype = self.select("loadTypeSelect").value

        if fileName[-4:].lower() not in [".txt", ".npz"]:
            fileName = fileName + filetype

        # initialize empty arrays or arrays with previous data to which new
        # data will be appended
        if overwriteData:
            resRPrev: NDArray[np.float64] = np.ndarray((0,), dtype=float)
            resIPrev: NDArray[np.float64] = np.ndarray((0,), dtype=float)
            orderPrev: NDArray[np.int32] = np.ndarray((0,), dtype=int)
            errRPrev: NDArray[np.float64] = np.ndarray((0,), dtype=float)
            errIPrev: NDArray[np.float64] = np.ndarray((0,), dtype=float)
            propErrRPrev: NDArray[np.float64] = np.ndarray((0,), dtype=float)
            propErrIPrev: NDArray[np.float64] = np.ndarray((0,), dtype=float)
            idxPrev: NDArray[np.int32] = np.ndarray((0,), dtype=int)
            filePrev: NDArray[np.str_] = np.ndarray((0,), dtype=str)
            numFiles: int = 0
        else:
            resRPrev = self.source.data["resR"]
            resIPrev = self.source.data["resI"]
            orderPrev = self.source.data["order"]
            errRPrev = self.source.data["errR"]
            errIPrev = self.source.data["errI"]
            propErrRPrev = self.source.data["propErrR"]
            propErrIPrev = self.source.data["propErrI"]
            idxPrev = self.source.data["idx"]
            filePrev = self.source.data["file"]
            numFiles = len(np.unique(filePrev))
            if len(constants.MARKERS) == numFiles:
                self.select("feedbackDiv").text = (
                    f"<p {constants.STR_STYLE_RED}>The maximum number of files"
                    + " is loaded.</p>"
                    + constants.STR_CLEAR_EXPLAIN
                )
                self.updateButtonStyles(warning="loadButton")
                return

        # load data from file
        try:
            loadDict = fromFile(fileName, filetype)
        except TypeError:
            self.select("feedbackDiv").text = (
                f"<p {constants.STR_STYLE_RED}>The file {fileName} does not "
                "contain data in the expected format</p>"
            )
            self.updateButtonStyles(warning="loadButton")
            return
        except FileNotFoundError:
            self.select("feedbackDiv").text = (
                f"<p {constants.STR_STYLE_RED}>No file  with name {fileName} "
                "found in the current working directory</p>"
                "<p>Use the above widget to change the current working "
                "directory."
            )
            self.updateButtonStyles(warning="loadButton")
            return

        # check compatibility with previous data
        surfaceMatch = (
            True
            if overwriteData
            else np.all(
                np.isclose(
                    loadDict["generators"],
                    self.handlerData["generators"],
                    rtol=1e-7,
                )
            )
        )

        if not surfaceMatch:
            self.select("feedbackDiv").text = (
                f"<p {constants.STR_STYLE_RED}>Loaded resonances belong to "
                "another Schottky surface. Please choose another file, or "
                "overwrite the currently displayed data.</p>"
            )
            self.updateButtonStyles(warning="loadButton")
            return

        # append data to the arrays intialised above
        resR = np.concatenate((resRPrev, loadDict["resonances"].real))
        resI = np.concatenate((resIPrev, loadDict["resonances"].imag))
        order = np.concatenate((orderPrev, loadDict["orders"]))
        errR = np.concatenate((errRPrev, loadDict["errors"].real))
        errI = np.concatenate((errIPrev, loadDict["errors"].imag))
        propErrR = np.concatenate(
            (propErrRPrev, loadDict["propagatedErrors"].real)
        )
        propErrI = np.concatenate(
            (propErrIPrev, loadDict["propagatedErrors"].imag)
        )
        numNewRes = len(loadDict["resonances"].real)
        idx = np.concatenate(
            (idxPrev, np.array(range(len(idxPrev), numNewRes + len(idxPrev))))
        )
        fileName = fileName if len(fileName) < 18 else "..." + fileName[-15:]
        fileName = str(numFiles + 1) + ": " + fileName
        file = np.concatenate((filePrev, np.full((numNewRes,), fileName)))

        # update ColumnDataSource object
        self.source.data = {
            "resR": resR,
            "resI": resI,
            "order": order,
            "errR": errR,
            "errI": errI,
            "absErr": abs(errR + 1j * errI),
            "propErrR": propErrR,
            "propErrI": propErrI,
            "absPropErr": abs(propErrR + 1j * propErrI),
            "idx": idx,
            "file": file,
        }

        # update dictionary storing metadata from the file
        if overwriteData:
            self.handlerData["generators"] = loadDict["generators"]
            self.handlerData["surfaceName"] = loadDict["surfaceName"]
            self.handlerData["zetaSettings"] = loadDict["zetaSettings"]
            self.handlerData["rfSettings"] = loadDict["rfSettings"]

        self.select("feedbackDiv").text = (
            f"<p {constants.STR_STYLE_GREEN}>Successfully loaded data from "
            + "file.</p>"
            + constants.STR_SELECT_EXPLAIN
        )
        if numFiles > 0:
            self.select("feedbackDiv").text += constants.STR_CLEAR_EXPLAIN
        self.updateButtonStyles(success="loadButton")

    def setupEmptyPlotData(self) -> None:
        "Set up default plotting data for 'empty' plot."
        # set up default data
        errR = np.random.rand(constants.DEFAULT_RES_R.size) * 0.9 + 0.1
        errI = np.random.rand(constants.DEFAULT_RES_R.size) * 0.9 + 0.1
        absErr = abs(errR + 1j * errI)

        propErrR = errR + np.random.rand(constants.DEFAULT_RES_R.size) * 0.1
        propErrI = errI + np.random.rand(constants.DEFAULT_RES_R.size) * 0.1
        absPropErr = abs(propErrR + 1j * propErrI)

        order = np.random.randint(1, 5, constants.DEFAULT_RES_R.size)
        idx = np.array(range(len(constants.DEFAULT_RES_R)))
        file = np.full(constants.DEFAULT_RES_R.shape, "PyZeta Logo")

        # update ColumnDataSource object
        self.source.data = {
            "resR": constants.DEFAULT_RES_R,
            "resI": constants.DEFAULT_RES_I,
            "order": order,
            "errR": errR,
            "errI": errI,
            "absErr": absErr,
            "propErrR": propErrR,
            "propErrI": propErrI,
            "absPropErr": absPropErr,
            "idx": idx,
            "file": file,
        }

        # update dictionary storing metadata from the file
        self.handlerData = {}

        self.select("feedbackDiv").text = constants.STR_LOAD_EXPLAIN
        self.updateButtonStyles(success="loadButton")

    def clearFile(self) -> None:
        "Clear data from a specific file from the plot."
        # retrieve fileName
        fileName = (
            self.select("loadText").value.strip()
            or self.select("loadText").placeholder
        )
        filetype = self.select("loadTypeSelect").value

        # find number of the file to be removed
        existingNames = np.sort(np.unique(self.source.data["file"]))
        fileNumber = 0

        if fileName.isdigit() and len(fileName) == 1:
            fileNumber = int(fileName)
        else:
            if fileName[-4:].lower() not in [".txt", ".npz"]:
                fileName = fileName + filetype

            fileName = (
                fileName if len(fileName) < 18 else "..." + fileName[-15:]
            )
            for existingName in existingNames:
                if fileName == existingName[3:]:
                    fileNumber = int(existingName[0])
                    break

        if fileNumber not in range(1, len(existingNames) + 1):
            self.select("feedbackDiv").text = (
                f"<p {constants.STR_STYLE_RED}>Not able to identify which file"
                " should be removed from the plot. Please enter either the "
                "name of the file or its number from the legend.</p>"
            )
            self.updateButtonStyles(warning="loadButton")
            return

        # fetch currently stored data from all files
        resR = self.source.data["resR"]
        resI = self.source.data["resI"]
        order = self.source.data["order"]
        errR = self.source.data["errR"]
        errI = self.source.data["errI"]
        propErrR = self.source.data["propErrR"]
        propErrI = self.source.data["propErrI"]
        idx = self.source.data["idx"]
        allNames = self.source.data["file"]

        self.select("scat").data_source.selected.indices = []

        # create a mask indicating which datapoints should be kept (= True)
        # and which must be removed (= False)
        mask = np.full_like(resR, True, dtype=bool)
        for i, name in enumerate(allNames):
            if fileNumber == int(name[0]):
                mask[i] = False
            elif fileNumber < int(name[0]):
                allNames[i] = str(int(name[0]) - 1) + allNames[i][1:]

        # store all datapoints that should be kept while removing the rest
        self.source.data = {
            "resR": resR[mask],
            "resI": resI[mask],
            "order": order[mask],
            "errR": errR[mask],
            "errI": errI[mask],
            "absErr": abs(errR + 1j * errI)[mask],
            "propErrR": propErrR[mask],
            "propErrI": propErrI[mask],
            "absPropErr": abs(propErrR + 1j * propErrI)[mask],
            "idx": idx[mask],
            "file": allNames[mask],
        }

        self.select("feedbackDiv").text = (
            f"<p {constants.STR_STYLE_GREEN}>Successfully cleared data from"
            + " plot.</p>"
            + constants.STR_SELECT_EXPLAIN
        )
        self.updateButtonStyles(success="loadButton")

    def updateData(self, mode: str) -> None:
        """
        Update plotting data.

        :param mode: indicate whether new data should overwrite current data,
            or new data be appended to current data, or current data be cleared
            or data from a specific file be cleared
        """
        # either overwrite previous data with new data from file
        if mode == "overwrite":
            self.loadData(overwriteData=True)

        # or add new data from file to previous data
        elif mode == "add":
            if len(self.handlerData) == 0:
                self.updateData(mode="overwrite")
            else:
                self.loadData(overwriteData=False)

        # or clear data from a specific file from plot
        elif mode == "clearSpecific":
            if len(np.unique(self.source.data["file"])) < 2:
                self.updateData(mode="clear")
            else:
                self.clearFile()

        # or clear all data from plot
        elif mode == "clear":
            self.setupEmptyPlotData()

        # update figure
        if self.select("loadButton").button_type == "success":
            self.updateFigure()

    def saveData(self) -> None:
        "Save selected data to file."
        # retrieve fileName
        fileName = (
            self.select("saveText").value.strip()
            or self.select("saveText").placeholder
        )
        filetype = self.select("saveTypeSelect").value

        if fileName[-4:].lower() not in [".txt", ".npz"]:
            fileName = fileName + filetype

        # check if metadata can be found (otherwise plot contains only the
        # default data)
        if len(self.handlerData) == 0:
            self.select("feedbackDiv").text = (
                f"<p {constants.STR_STYLE_RED}>An error occured. It seems "
                + "like the plotted data does not belong to any Schottky "
                + "Surface and thus can not be saved.</p>"
                + constants.STR_LOAD_EXPLAIN
            )
            self.updateButtonStyles(warning="saveButton")
            return

        # prepare data for saving
        saveDict = {}
        saveDict["generators"] = self.handlerData["generators"]
        saveDict["surfaceName"] = self.handlerData["surfaceName"]
        saveDict["zetaSettings"] = self.handlerData["zetaSettings"]
        saveDict["rfSettings"] = self.handlerData["rfSettings"]

        res = self.source.data["resR"] + 1j * self.source.data["resI"]
        order = self.source.data["order"]
        err = self.source.data["errR"] + 1j * self.source.data["errI"]
        propErr = (
            self.source.data["propErrR"] + 1j * self.source.data["propErrI"]
        )

        select = self.select("scat").data_source.selected.indices
        if len(select) == 0:
            select = list(range(len(res)))

        saveDict["resonances"] = res[select]
        saveDict["orders"] = order[select]
        saveDict["errors"] = err[select]
        saveDict["propagatedErrors"] = propErr[select]

        # check if an existing file might be overwritten by accident
        overwriteFile = self.select("saveButton").label == "Overwrite"

        # save data to file
        try:
            toFile(
                fileName,
                saveDict,
                filetype=filetype,
                allowOverwrite=overwriteFile,
            )
            self.select("feedbackDiv").text = (
                f"<p {constants.STR_STYLE_GREEN}>Successfully saved to "
                f"{fileName}.</p>"
            )
            self.updateButtonStyles(success="saveButton")
            self.select("saveButton").label = "Save data"
        except FileExistsError:
            self.select("feedbackDiv").text = (
                f"<p {constants.STR_STYLE_RED}>File {fileName} already exists."
                " Please confirm overwrite or enter a new fileName.</p>"
            )
            self.updateButtonStyles(warning="saveButton")
            self.select("saveButton").label = "Overwrite"

    def updateIndices(self, new: Optional[List[int]] = None) -> None:
        "Update ordering of the data points."
        if new is None:
            new = self.select("scat").data_source.selected.indices

        numRes = self.source.data["resR"].size

        if len(new) == 0:  # no resonances are selected
            self.source.data["idx"] = np.array(range(numRes))
            self.select("feedbackDiv").text = (
                constants.STR_SELECT_EXPLAIN + constants.STR_LOAD_EXPLAIN
            )
        else:  # some resonances are selected
            idx = np.full((numRes,), numRes - 1, dtype=int)
            idx[new] = list(range(len(new)))
            self.source.data["idx"] = idx
            self.select("feedbackDiv").text = (
                constants.STR_SAVE_REMINDER + constants.STR_DESELECT_EXPLAIN
            )

        if len(np.unique(self.source.data["file"])) > 1:
            self.select("feedbackDiv").text += constants.STR_CLEAR_EXPLAIN

        self.updateButtonStyles()
        self.select("saveButton").label = "Save data"

    def updateCWD(self) -> None:
        "Change the current working directory."
        newDir = self.select("cwdText").value

        if newDir in [os.getcwd(), ".", os.sep]:  # newdir is equal to cwd
            self.select("cwdText").value = os.getcwd()
            self.updateIndices()

        elif os.path.exists(newDir):  # change cwd to newDir
            os.chdir(newDir)
            cwd = os.getcwd()
            self.select("cwdText").value = cwd
            if len(cwd) > 40:
                cwd = "..." + cwd[-37:]
            self.select("feedbackDiv").text = (
                f"<p {constants.STR_STYLE_GREEN}>Successfully changed working "
                f"directory to '{cwd}'.</p>"
            )
            self.updateButtonStyles(success="cwdButton")

        else:  # newDir does not exist
            self.select("feedbackDiv").text = (
                f"<p {constants.STR_STYLE_RED}>The chosen directory does not"
                " exist. Please enter a valid path.</p>"
            )
            self.updateButtonStyles(warning="cwdButton")

    def plot(self) -> None:
        "Set up all dynamic functionality of the bokeh document."
        # plot default initial data
        self.updateData("clear")
        self.updateFigure()
        self.updateButtonStyles()

        # add callback to the event of change of selection of data points
        self.select("scat").data_source.selected.on_change(
            "indices", lambda _, __, new: self.updateIndices(new)
        )

        # add callbacks to all widgets
        self.select("colorCodeSelect").on_change(
            "value",
            lambda _, __, ___: self.updateFigure(),
            lambda _, __, ___: self.updateIndices(),
        )

        self.select("colorMapSelect").on_change(
            "value",
            lambda _, __, ___: self.updateFigure(),
            lambda _, __, ___: self.updateIndices(),
        )

        self.select("saveText").on_change(
            "value_input", lambda _, __, ___: self.updateIndices()
        )

        self.select("loadButton").on_event(
            MenuItemClick, lambda click: self.updateData(click.item)
        )

        self.select("saveButton").on_click(lambda _: self.saveData())

        self.select("cwdButton").on_click(lambda _: self.updateCWD())

        # create dynamic bokeh document
        curdoc().add_root(self.layout)
        curdoc().title = "PyZeta -- Resonance Selector Tool"
        curdoc().theme = "caliber"


# To view the dynamic bokeh document, run
#  $ python -m bokeh serve selector.py --dev --show
# in the console

if __name__[:5] == "bokeh":
    # create static bokeh document
    selector = ResonanceSelector()
    # make it dynamic
    selector.plot()
