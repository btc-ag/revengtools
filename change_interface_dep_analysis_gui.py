#!/usr/bin/python
# -*- coding: utf-8 -*-

import wx

from change_interface_dep_analysis import SVNAndInterfaceDepAnalyzer
import logging
import sys
import pickle
import datetime
import time
import commons.fileselection
import os.path

class SearchAndAddWindow(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self,parent, title="Suchen und hinzufügen")
        paddingSizer = wx.BoxSizer(wx.VERTICAL)
        box = wx.FlexGridSizer(3,3,5,5)
        box.Add(wx.StaticText(self,label="Surchordner:"))
        self.pathTextCtrl = wx.TextCtrl(self,size=(250,-1))
        box.Add(self.pathTextCtrl)
        selectButton = wx.Button(self,label="Auswählen")
        selectButton.Bind(wx.EVT_BUTTON, self.on_dir_select) 
        box.Add(selectButton)
        box.Add(wx.StaticText(self,label="RegEx-Pattern:"))
        self.fileExtensionsTextCtrl = wx.TextCtrl(self,size=(250,-1))
        box.Add(self.fileExtensionsTextCtrl)
        box.Add(wx.StaticText(self))
        box.Add(wx.StaticText(self,label="Beispiel:"))
        box.Add(wx.StaticText(self,label="BTC\.CAB.*\.dll"))
        paddingSizer.Add(box,1,wx.ALL,10)
        paddingSizer.Add(wx.Button(self,wx.ID_OK, label="Hinzufügen"),0,wx.ALIGN_RIGHT | wx.RIGHT | wx.BOTTOM,10)
        self.SetSizer(paddingSizer)
        self.Fit()
        self.Center()
    def on_dir_select(self, event):
        dlg = wx.DirDialog(self,style=wx.DD_DIR_MUST_EXIST|wx.THICK_FRAME)
        res = dlg.ShowModal()
        if res == wx.ID_OK:
            self.pathTextCtrl.SetValue(dlg.GetPath())
    def getFiles(self):
        if os.path.exists(self.pathTextCtrl.GetValue()):
            return commons.fileselection.find_files_with_filename_regex(self.pathTextCtrl.GetValue(), self.fileExtensionsTextCtrl.GetValue())
        else:
            raise ""

class NewAnalysisFileSelectionFrame(wx.Panel):
    def __init__(self, parent, text):
        wx.Panel.__init__(self,parent)
        hBox = wx.BoxSizer(wx.VERTICAL)
        hBox.Add(wx.StaticText(self,label=text))
        self.fileList = wx.ListBox(self,style=wx.LB_EXTENDED)
        self.fileList.SetSizeHints(500,160)
        hBox.Add(self.fileList,1,wx.EXPAND)
        vBox = wx.BoxSizer(wx.HORIZONTAL)
        addButton = wx.Button(self,label="+")
        addButton.Bind(wx.EVT_BUTTON,self.on_add_click)
        addWildcardButton = wx.Button(self,label="Suchen und hinz.")
        addWildcardButton.Bind(wx.EVT_BUTTON, self.on_search_and_add_click)
        delButton = wx.Button(self,label="-")
        delButton.Bind(wx.EVT_BUTTON,self.on_del_click)
        vBox.Add(addButton)
        vBox.AddSpacer(5)
        vBox.Add(addWildcardButton)
        vBox.AddSpacer(5)
        vBox.Add(delButton)
        hBox.Add(vBox)
        self.SetSizer(hBox)
    def __add_files_and_merge(self, fileList):
        alreadyLoadedFiles = self.fileList.GetItems()
        self.fileList.AppendItems([i for i in fileList if i not in alreadyLoadedFiles])
    def on_search_and_add_click(self, event):
        dlg = SearchAndAddWindow(self)
        res = dlg.ShowModal()
        if res == wx.ID_OK:
            files = dlg.getFiles()
            self.__add_files_and_merge(files)
    def on_add_click(self, event):
        dlg = wx.FileDialog(self,"Datei auswählen","","","CSharp-Dateien (*.cs)|*.cs|Quelltextdateilisten (*.txt)|*.txt|Alle Dateien (*.*)|*.*",wx.OPEN)
        res = dlg.ShowModal()
        if res == wx.ID_OK:
            path = dlg.GetPath()
            if path.endswith(".txt"):
                loadedFileList = parseFileList(path)
                self.__add_files_and_merge(loadedFileList)
            else:
                if path not in self.fileList.GetItems():
                    self.fileList.Append(path)
    def on_del_click(self, event):
        selectedItems = self.fileList.GetSelections()
        for i,pos in enumerate(selectedItems):
            self.fileList.Delete(pos-i)
    def getFiles(self):
        return self.fileList.GetItems()
            

class NewAnalsysisWindow(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self,parent, title="Neue Analyse")
        mainBox = wx.BoxSizer(wx.VERTICAL)
        
        #Controls for picking the analysis time range
        startTime = datetime.datetime.now() - datetime.timedelta(days=120)
        self.startTimePicker = wx.DatePickerCtrl(self,dt=wx.DateTimeFromTimeT(time.mktime(startTime.timetuple())))
        self.endTimePicker = wx.DatePickerCtrl(self) 
        
        mainBox.Add(wx.StaticText(self,label="SVN-Analysezeitraum festlegen:"),0,wx.ALL,10)
        timeChooseBox = wx.BoxSizer(wx.HORIZONTAL)
        timeChooseBox.Add(wx.StaticText(self,label="Begin:"),0,wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 10)
        timeChooseBox.Add(self.startTimePicker,0,wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 10)
        timeChooseBox.Add(wx.StaticText(self,label="Ende:"),0,wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 10)
        timeChooseBox.Add(self.endTimePicker,0,wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 10)
        mainBox.Add(timeChooseBox)
        
        self.left_src_frame = NewAnalysisFileSelectionFrame(self,"Quelltext Dateien") 
        mainBox.Add(self.left_src_frame,1,wx.ALL,10)
        self.left_dll_frame = NewAnalysisFileSelectionFrame(self,"DLLs")
        mainBox.Add(self.left_dll_frame,1,wx.ALL,10)
        self.right_dll_frame = NewAnalysisFileSelectionFrame(self,"Schnittstellenanalyse DLLs") 
        mainBox.Add(self.right_dll_frame,1,wx.ALL,10)
        
        #Do Analysis Button
        mainBox.Add(wx.Button(self,wx.ID_OK,"Analyse durchführen"),0,wx.ALIGN_RIGHT | wx.ALL, 10)
        
        print self.startTimePicker.GetValue().GetTicks()
        
        self.SetSizer(mainBox)
        self.Fit()
        self.Center()
    def get_analysis_time_range(self):
        return (datetime.datetime.fromtimestamp(self.startTimePicker.GetValue().GetTicks()), datetime.datetime.fromtimestamp(self.endTimePicker.GetValue().GetTicks()))
    def get_left_source_files(self):
        return self.left_src_frame.getFiles()
    def get_left_dll_files(self):
        return self.left_dll_frame.getFiles()
    def get_right_dll_files(self):
        return self.right_dll_frame.getFiles()

#TODO Remove this function! It's already definied in InterfaceDepAnalyse.py
def parseFileList(fileName):
    f = open(fileName,"r")
    res = []
    for line in f.readlines():
        #Check if line is empty
        line = line.rstrip("\n")
        if line:
            res.append(line)
    return res

class ModuleSubdisplayPanelEntry(wx.Panel):
    def __init__(self, parent, item, selection_change_handler = None):
        wx.Panel.__init__(self, parent, style=wx.BORDER,size=(200,30))
        self.SetBackgroundColour(wx.WHITE)
        contentBox = wx.BoxSizer(wx.VERTICAL)
        contentBox.Add(wx.StaticText(self, label=self.__format_box_string(item)), 0, wx.ALL, 10)
        self.item = item
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseDown)
        #Hack, shouldn't be necessary...
        for item in contentBox.GetChildren():
            item.GetWindow().Bind(wx.EVT_LEFT_DOWN, self.OnMouseDown)
        self.SetSizer(contentBox)
        self.selected = False
        self.handler = selection_change_handler
    def __format_box_string(self, changeInterfaceResult):
        changes = changeInterfaceResult.Changes
        if changeInterfaceResult.Changes is None:
            changes = "Unbekannt"
        return "{0} (IDeps: {1} Changes: {2})".format(changeInterfaceResult.Name,len(changeInterfaceResult.IDeps),changes)
    def getSelectionState(self):
        return self.selected
    def getModule(self):
        return self.item
    def OnMouseDown(self, evt):
        if not self.selected:
            self.SetBackgroundColour(wx.Color(143,190,255))
        else:
            self.SetBackgroundColour(wx.WHITE)
        #Toggle
        self.selected = not self.selected
        self.Refresh()
        if self.handler is not None:
            self.handler()
        

class ModuleSubdisplayPanel(wx.Panel):
    PADDING = 10
    BOX_HEIGHT = 30
    def __init__(self, parent, color, title, entrySelectionChangedHandler):
        wx.Panel.__init__(self,parent)
        
        self.entrySelectionChangedHandler = entrySelectionChangedHandler
        
        #Set default Font
        self.FONT = wx.Font(10,wx.FONTFAMILY_DEFAULT,wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_LIGHT)
        
        #Get a sizer with one element to maximize the client panel
        box = wx.BoxSizer(wx.VERTICAL)
        label = wx.StaticText(self,label=title, style=wx.ALIGN_CENTRE)
        f = label.GetFont()
        f.SetWeight(wx.BOLD)
        label.SetFont(f)
        box.Add(label,0,wx.ALIGN_CENTER_HORIZONTAL | wx.EXPAND)
        self.scroll = wx.ScrolledWindow(self)
        box.Add(self.scroll,1,wx.EXPAND)
        self.content = wx.Panel(self.scroll,-1)
        contentBox = wx.BoxSizer(wx.VERTICAL)
        contentBox.Add(self.content,1,wx.EXPAND | wx.ALL)
        self.SetBackgroundColour(color)
        self.moduleList = []
        self.moduleEntryPanelList = []
        
        #Sizer for the list ModuleSubdisplayPanelEntry in this panel
        self.contentBox = wx.BoxSizer(wx.VERTICAL)
        self.content.SetSizer(self.contentBox)
        
        self.scroll.SetSizer(contentBox)
        self.SetSizer(box)
        self.scroll.SetScrollRate(1,1)
    def setModuleList(self, moduleList):
        self.moduleList = []
        self.contentBox.Clear(True)
        self.moduleEntryPanelList = []
        for m in moduleList:
            entryPanel = ModuleSubdisplayPanelEntry(self.content,m, self.entrySelectionChangedHandler)
            self.moduleEntryPanelList.append(entryPanel)
            self.contentBox.Add(entryPanel,0, wx.TOP | wx.LEFT, 20)
            self.moduleList.append(m)
        self.contentBox.Layout()
        self.scroll.FitInside()
    def getSelectedModules(self):
        res = []
        for i in self.moduleEntryPanelList:
            if i.getSelectionState():
                res.append(i.getModule())
        return res
    def getModuleList(self):
        return self.moduleList
    
class ModuleDisplayPanel(wx.Panel):
    def __init__(self, parent, selectionChangedHandler, thresholdIDep = 0, thresholdChanges = 0):
        wx.Panel.__init__(self, parent,style=wx.BORDER)
        self.SetBackgroundColour(wx.WHITE)
        self.grid = wx.GridSizer(cols=2,rows=2)
        
        self.areas = []
        configs = [
                   ("hohe Änderungsrate / viele IDeps", wx.RED), 
                   ("hohe Änderungsrate / wenig IDeps", wx.Color(255,208,0)),
                   ("geringe Änderungsrate / viele IDeps", wx.Color(255,208,0)),
                   ("geringe Änderungsrate / wenig IDeps", wx.GREEN)
                  ]
        for config in configs:
            (title, color) = config
            print color
            subdisplay = ModuleSubdisplayPanel(self, color, title, selectionChangedHandler)
            self.grid.Add(subdisplay,0,wx.EXPAND)
            self.areas.append(subdisplay)

        self.SetSizer(self.grid)
        self.thresholdChange = thresholdIDep
        self.thresholdIDep = thresholdChanges   
    def setThresholds(self,idepValue,changeValue):
        self.thresholdIDep = idepValue
        self.thresholdChange = changeValue
        self.__resortModules()
    def getThresholds(self):
        return (self.thresholdIDep, self.thresholdChange)
    def getSelectedModules(self):
        return [item for area in self.areas for item in area.getSelectedModules()]
    def __resortModules(self):
        allModules = []
        #Collect and delete 
        for area in self.areas:
            allModules.extend(area.getModuleList())
        self.__sortModules(allModules)
    def __sortModules(self, moduleList):
        self.areas[0].setModuleList(filter(lambda m: len(m.IDeps) >= self.thresholdIDep and m.Changes >= self.thresholdChange, moduleList))
        self.areas[1].setModuleList(filter(lambda m: len(m.IDeps) < self.thresholdIDep and m.Changes >= self.thresholdChange, moduleList))
        self.areas[2].setModuleList(filter(lambda m: len(m.IDeps) >= self.thresholdIDep and m.Changes < self.thresholdChange, moduleList))
        self.areas[3].setModuleList(filter(lambda m: len(m.IDeps) < self.thresholdIDep and m.Changes < self.thresholdChange, moduleList))
    def setModuleList(self, moduleList):
        self.__sortModules(moduleList)
        
class OperationAbortError(Exception):
    """Thrown when a action in the user interface is aborted by the user"""
    pass

class MainFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, title="Change Interface Dep Analysis Tool")
        mainPanel = wx.Panel(self, -1)
        
        self.build_menu_bar()
        
        controlPanel = wx.Panel(mainPanel)
        
        self.drawPanel = ModuleDisplayPanel(mainPanel, self.OnSelectionChange,1,1)
        self.usedInList = wx.ListBox(mainPanel)
        self.currentAnalysisResult = []
        
        (idepThres, changesThres) = self.drawPanel.getThresholds()
        self.thresholdIDepSpinner = wx.SpinCtrl(controlPanel)
        self.thresholdIDepSpinner.SetValue(idepThres)
        self.thresholdIDepSpinner.Bind(wx.EVT_SCROLL, self.OnThresholdChanged)
        self.thresholdChangesSpinner = wx.SpinCtrl(controlPanel)
        self.thresholdChangesSpinner.SetValue(changesThres)
        self.thresholdChangesSpinner.Bind(wx.EVT_SCROLL, self.OnThresholdChanged)
        
        vBox = wx.BoxSizer(wx.VERTICAL)
        vBox.AddSpacer(20)
        
        controlBox = wx.BoxSizer(wx.HORIZONTAL)
        controlBox.AddSpacer(20)
        controlBox.Add(wx.StaticText(controlPanel, label=u"Schwellenwert Schnittstellenabhängigkeiten:"),0,wx.ALIGN_CENTER)
        controlBox.AddSpacer(10)

        controlBox.Add(self.thresholdIDepSpinner,0,10)
        controlBox.AddSpacer(10)
        controlBox.Add(wx.StaticText(controlPanel, label=u"Schwellenwert Änderungen:"),0,wx.ALIGN_CENTER)
        controlBox.AddSpacer(10)
        controlBox.Add(self.thresholdChangesSpinner,0)
        controlBox.AddSpacer(10)
        
        vBox.Add(controlBox)
        controlPanel.SetSizer(vBox)
        
        self.bottomHBox = wx.BoxSizer(wx.HORIZONTAL)
        self.bottomHBox.Add(self.drawPanel,1,wx.EXPAND | wx.ALL)
        self.bottomHBox.AddSpacer(20)
        leftVBox = wx.BoxSizer(wx.VERTICAL)
        leftVBox.Add(wx.StaticText(mainPanel,label="verwendet in Schnittstellen:"))
        leftVBox.AddSpacer(5)
        leftVBox.Add(self.usedInList)
        self.bottomHBox.Add(leftVBox,0)
        
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(controlPanel,0, wx.EXPAND)
        box.Add(self.bottomHBox,1, wx.ALL | wx.EXPAND,20)
        mainPanel.SetSizer(box)
        self.SetSize((800,600))
        self.Show()
    def build_menu_bar(self):
        menubar = wx.MenuBar()
        fileMenu = wx.Menu()
        newAnalysisMenuEntry = fileMenu.Append(wx.ID_ANY, 'Neue Analyse')
        loadResultMenuEntry = fileMenu.Append(wx.ID_ANY, 'Ergebnis laden')
        saveResultMenuEntry = fileMenu.Append(wx.ID_ANY, 'Ergebnis speichern')
        menubar.Append(fileMenu, '&Datei')
        self.SetMenuBar(menubar)
        
        self.Bind(wx.EVT_MENU, self.on_new_analysis, newAnalysisMenuEntry)
        self.Bind(wx.EVT_MENU, self.on_load_result, loadResultMenuEntry)
        self.Bind(wx.EVT_MENU, self.on_save_result, saveResultMenuEntry)
    def on_new_analysis(self, evt):
        dlg = NewAnalsysisWindow(self)
        res = dlg.ShowModal()
        if res == wx.ID_OK:
            (start,end) = dlg.get_analysis_time_range() 
            self.do_analyze(dlg.get_left_source_files(), dlg.get_left_dll_files(), dlg.get_right_dll_files(), start, end)
    def on_load_result(self, evt):
        try:
            path = self.__show_file_dialog(wx.OPEN)
            resFile = open(path,"r")
            analysisResult = pickle.load(resFile)
            self.drawPanel.setModuleList(analysisResult)
            resFile.close()
        except OperationAbortError:
            #Do nothing on user abort
            pass
    def on_save_result(self, evt):
        try:
            path = self.__show_file_dialog(wx.SAVE)
            resFile = open(path,"w")
            pickle.dump(self.currentAnalysisResult, resFile)
            resFile.close()
        except OperationAbortError:
            #Do nothing on user abort
            pass
    def __show_file_dialog(self, dlgType):
        if dlgType == wx.SAVE:
            title = "Analyseergebnis speichern"
        else:
            title = "Analyseergebnis laden"
        dlg = wx.FileDialog(self,title,"","","Analyseergebnisse (*.anares)|*.anares|Alle Dateien (*.*)|*.*",wx.OPEN)
        res = dlg.ShowModal()
        if res == wx.ID_OK:
            return dlg.GetPath()
        else:
            raise OperationAbortError()
    def OnSelectionChange(self):
        selected = self.drawPanel.getSelectedModules()
        self.usedInList.Clear()
        self.usedInList.SetItems([idep for m in selected for idep in m.IDeps])
        
        #Make the ListBox bigger if necessary
        self.bottomHBox.Layout()
    def OnThresholdChanged(self, evt):
        self.drawPanel.Show(False)
        self.drawPanel.setThresholds(self.thresholdIDepSpinner.GetValue(), self.thresholdChangesSpinner.GetValue())
        self.drawPanel.Show()
    def do_analyze(self,srcList,srcDll,rightSide, startDate, endDate):
        #Analyse files
        analyzer = SVNAndInterfaceDepAnalyzer()
        self.currentAnalysisResult = analyzer.interface_dependency_analyse(srcList,srcDll,rightSide, startDate, endDate)
        
        #Test Data
        #res = [
        #       ChangeInterfaceAnaysisResult("Test","Test.txt",3,2),
        #       ChangeInterfaceAnaysisResult("Test","Test.txt",3,2),
        #       ChangeInterfaceAnaysisResult("Test","Test.txt",0,2),
        #       ChangeInterfaceAnaysisResult("Test","Test.txt",3,5),
        #       ChangeInterfaceAnaysisResult("Test","Test.txt",4,2),
        #       ]
        
        #Display
        self.drawPanel.setModuleList(self.currentAnalysisResult)

if __name__ == "__main__":
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    app = wx.App(False)
    MainFrame(None)
    app.MainLoop()
