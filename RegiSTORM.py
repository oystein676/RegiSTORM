import PySimpleGUI as sg
import os
import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors
import time
from joblib import Parallel, delayed
import scipy.spatial as spatial
import itertools
import multiprocessing
from modules.MCR import *


from joblib import parallel_backend
parallel_backend("threading")

import os
import sys
try:
    # Python 3.4+
    if sys.platform.startswith('win'):
        import multiprocessing.popen_spawn_win32 as forking
    else:
        import multiprocessing.popen_fork as forking
except ImportError:
    import multiprocessing.forking as forking


"""
    Restrict the characters allowed in an input element to digits and . or -
    Accomplished by removing last character input if not a valid character
"""

def check_partly_valid_positive_float(s):
    return (s == "." or check_positive_float(s)) and not (len(s) > 0 and s[-1] == " ")

def check_positive_float(s):
    try:
        v = float(s)
        isFloat = v >= 0
    except:
        isFloat = False
    return isFloat

def check_positive_int(s):
    return s.isdecimal() and int(s) > 0

def check_nonnegative_int(s):
    return s.isdecimal() and int(s) >= 0

def clear_task_list():
    task_name_list = []
    all_tasks_dictionary.clear()
    window1["listBox1"].update(task_name_list)

def add_task():
    edit_task()

def edit_task(task_name=""):
    global values2
    global values3
    global task_name_list
    global all_tasks_dictionary
    global file_list2
    if task_name != "" and task_name in all_tasks_dictionary:
        add_new = False
        fiducialSize = all_tasks_dictionary[task_name]['fiducialSize']
        varianceLimit = all_tasks_dictionary[task_name]['varianceLimit']
        meanTol = all_tasks_dictionary[task_name]['meanTol']
        resultsFolder = all_tasks_dictionary[task_name]['resultsFolder']
        resultsSuffix = all_tasks_dictionary[task_name]['resultsSuffix']
        file_list2 = all_tasks_dictionary[task_name]['File Names']
        selected = all_tasks_dictionary[task_name]['selected']
        #Advanced
        mode = all_tasks_dictionary[task_name]['mode']
        registrationTolerance = all_tasks_dictionary[task_name]['registrationTolerance']
        deleteFiducialsAfter = all_tasks_dictionary[task_name]['deleteFiducialsAfter']
        frameIntervals = all_tasks_dictionary[task_name]['frameIntervals']
    else:
        add_new = True
        fiducialSize = 100
        varianceLimit = 0.25
        meanTol = 0.5
        resultsFolder = ""
        resultsSuffix = "_corrected"
        file_list2 = []
        selected = []
        #Advanced
        mode = "Fiducial"
        registrationTolerance = 1
        deleteFiducialsAfter = True
        frameIntervals = []

    #Advanced settings default values
    mode = "Fiducial"
    registrationTolerance = 1
    deleteFiducialsAfter = True
    

    layout2 = [
        [sg.Text("Task definition (the name needs to be unique):"), sg.InputText(key="taskDefinitionText", default_text=task_name)],
        [sg.Text("Files (add at least two files, then select the reference file)")],
        [sg.Listbox(values=file_list2, enable_events=True, size=(100, 10), key="listBox2")],
        [sg.FilesBrowse(key="fileBrowse1", enable_events=True, file_types=(("CSV Files","*.csv"),))],
        [sg.Text("Fiducial size (nm)"), sg.Input(key="fiducialSize", default_text=fiducialSize, enable_events=True)],
        [sg.Text("Variance Limit"), sg.Input(key="varianceLimit", default_text=varianceLimit, enable_events=True)],
        [sg.Text("Mean Tolerance"), sg.Input(key="meanTol", default_text=meanTol, enable_events=True)],
        [sg.Button("Advanced Settings")],
        [sg.Text('Results folder:'), sg.Input(key='resultsFolder', default_text=resultsFolder), sg.FolderBrowse()],
        [sg.Text("Results suffix"), sg.InputText(key="resultsSuffix", default_text=resultsSuffix, enable_events=True)],
        [sg.Button("Add"), sg.Button("Cancel")]
    ]
    window2 = sg.Window(title="Add task", layout=layout2, finalize=True)

    if file_list2:
        window2["listBox2"].update(file_list2)
    doInit = True
    while True:
        event2, values2 = window2.read(timeout=300)
        if doInit:
            if file_list2:
                window2["listBox2"].update(file_list2)
            if selected:
                values2["listBox2"] = [selected]
            doInit = False

        if event2 in [sg.WIN_CLOSED, "Cancel"]:
            window2.close()
            break

        elif event2 == "Add":
            #Check valid input
            check2 = check_parameters2(add_new)
            if check2 == "OK":
                #File_Names=[os.path.basename(os.path.normpath(file)) for file in file_list2]
                if values2["taskDefinitionText"] not in task_name_list:
                    task_name_list += [values2["taskDefinitionText"]]
                window1["listBox1"].update(task_name_list)
                task_dictionary = {"name": values2["taskDefinitionText"], "fileList": file_list2,
                                   "selected": values2["listBox2"][0], "fiducialSize": values2["fiducialSize"],
                                   "File Names": file_list2,
                                   "varianceLimit": values2["varianceLimit"],
                                   "meanTol": values2["meanTol"],
                                   "resultsFolder": values2["resultsFolder"], "mode": mode,
                                   "registrationTolerance": registrationTolerance,
                                   "deleteFiducialsAfter": deleteFiducialsAfter,
                                   "frameIntervals": frameIntervals,
                                   "resultsSuffix": values2["resultsSuffix"]}
                all_tasks_dictionary[values2["taskDefinitionText"]] = task_dictionary
                window2.close()
            else:
                sg.popup("Input not correct:\n" + check2, title="Error!")

        elif event2 == "fileBrowse1":
            for file in values2["fileBrowse1"].split(';'):
                if os.path.exists(file):
                    if not file in file_list2:
                        file_list2 += [file]
                        frameIntervals += [('0', 'end')]
            window2["listBox2"].update(file_list2)

        elif event2 == "fiducialSize" and values2["fiducialSize"]:
            # if last character in input element is invalid, remove it
            if not check_partly_valid_positive_float(values2["fiducialSize"]):
                window2["fiducialSize"].update(values2["fiducialSize"][:-1])

        elif event2 == "varianceLimit" and values2["varianceLimit"]:
            # if last character in input element is invalid, remove it
            if not check_partly_valid_positive_float(values2["varianceLimit"]):
                window2["varianceLimit"].update(values2["varianceLimit"][:-1])
                
        elif event2 == "meanTol" and values2["meanTol"]:
            # if last character in input element is invalid, remove it
            if not check_partly_valid_positive_float(values2["meanTol"]):
                window2["meanTol"].update(values2["meanTol"][:-1])

        elif event2 == "Advanced Settings":
            layout3 = [
                [sg.Radio("Fiducial mode", "radioFiducialMode", key="radioFiducialMode", default=(mode=="Fiducial"), enable_events=True),
                 sg.Radio("Cluster mode", "radioClusterMode", key="radioClusterMode", default=(mode=="Cluster"), enable_events=True)],
                [sg.Text("Registration tolerance (sigma)"), sg.Input(key="registrationTolerance",
                                                                     default_text=registrationTolerance, enable_events=True)],
                [sg.Text("Delete fiducials after:"),
                 sg.Radio("Yes", "radioYes", key="radioYes", default=deleteFiducialsAfter, enable_events=True),
                 sg.Radio("No", "radioNo", key="radioNo", default=not deleteFiducialsAfter, enable_events=True)]
            ]
            maxlen = 0
            for i in range(len(file_list2)):
                maxlen = max(len(os.path.basename(os.path.normpath(file_list2[i]))), maxlen)

            layout3 += [[sg.Text("", size=(maxlen, 1)), sg.Text("Start frame", size=(10,1)), sg.Text("End frame", size=(11,1))]]
            for i in range(len(file_list2)):
                layout3 += [[sg.Text(os.path.basename(os.path.normpath(file_list2[i])), size=(maxlen, 1)),
                            sg.Input(key="startFrame" + str(i), default_text=frameIntervals[i][0], size=(11, 1), enable_events=True),
                            sg.Input(key="endFrame" + str(i), default_text=frameIntervals[i][1], size=(11, 1), enable_events=True)]]

            layout3 += [[sg.Button("Close")]]
            window3 = sg.Window(title="Advanced settings", layout=layout3, finalize=True)
            while True:
                event3, values3 = window3.read(timeout=300)
                if event3 in [sg.WIN_CLOSED, "Close"]:
                    check3 = check_parameters3()
                    if check3 == "OK":
                        mode = "Fiducial" if values3["radioFiducialMode"] else "Cluster"
                        registrationTolerance = values3["registrationTolerance"]
                        deleteFiducialsAfter = values3["radioYes"]
                        for i in range(len(file_list2)):
                            frameIntervals[i] = (values3["startFrame" + str(i)], values3["endFrame" + str(i)])

                        window3.close()
                        break
                    else:
                        sg.popup("Input not correct:\n" + check3, title="Error!")

                elif event3 == "radioFiducialMode":
                    window3["radioFiducialMode"].Update(value=True)
                    values3["radioFiducialMode"] = True
                    window3["radioClusterMode"].Update(value=False)
                    values3["radioClusterMode"] = False

                elif event3 == "radioClusterMode":
                    window3["radioClusterMode"].Update(value=True)
                    values3["radioClusterMode"] = True
                    window3["radioFiducialMode"].Update(value=False)
                    values3["radioFiducialMode"] = False

                elif event3 == "registrationTolerance" and values3["registrationTolerance"]:
                    # if last character in input element is invalid, remove it
                    if not check_positive_int(values3["registrationTolerance"]):
                        window3["registrationTolerance"].update(values3["registrationTolerance"][:-1])

                elif event3 == "radioYes":
                    window3["radioYes"].Update(value=True)
                    values3["radioYes"] = True
                    window3["radioNo"].Update(value=False)
                    values3["radioNo"] = False

                elif event3 == "radioNo":
                    window3["radioNo"].Update(value=True)
                    values3["radioNo"] = True
                    window3["radioYes"].Update(value=False)
                    values3["radioYes"] = False

def do_run():
    #TODO: Run all tasks
    #Note:
    success = False
    multiprocessing.freeze_support() #TEST IF HELP EXECUTION ISSUE
    try:
        for Job in all_tasks_dictionary:
            print('Running: ', Job)
            window1["textOutput"].Update(value="Running " + str(Job) + "\n", append=True)
            MCR(all_tasks_dictionary[Job], window1)
        success = True
    except Exception as e:
        print(e)
        window1["textOutput"].Update(value="Exception: " + str(e) + "\n", append=True)
    if success:
        #Clear the task list
        clear_task_list()


def check_parameters1():
    global all_tasks_dictionary
    return "OK" if len(all_tasks_dictionary) > 0 else "No tasks"

def check_parameters2(add_new):
    global values2
    global file_list2
    resultString = ""
    if len(values2["taskDefinitionText"]) == 0:
        resultString += "* Missing task definition.\n"
    if len(file_list2) < 2:
        resultString += "* You need to provide at least two files.\n"
    if len(values2["listBox2"]) == 0 or (len(values2["listBox2"]) > 0 and len(values2["listBox2"][0]) == 0):
        resultString += "* You need to select one file.\n"
    if add_new and values2["taskDefinitionText"] in all_tasks_dictionary.keys():
        resultString += "* Task name already exists.\n"
    if not check_positive_float(values2["fiducialSize"]):
        resultString += "* Missing Fiducial size.\n"
    if not check_positive_float(values2["varianceLimit"]):
        resultString += "* Missing Variance limit.\n"
    if not check_positive_float(values2["meanTol"]):
        resultString += "* Missing Mean Tolerance.\n"
    if not os.path.isdir(values2["resultsFolder"]):
        resultString += "* Invalid Results folder.\n"
    if len(values2["resultsSuffix"]) == 0:
        resultString += "* Invalid Results suffix.\n"

    if resultString == "":
        resultString = "OK"

    return resultString

def check_parameters3():
    global values3
    global file_list2
    resultString = ""
    if not check_positive_int(values3["registrationTolerance"]):
        resultString += "* Invalid Registration tolerance"
    for i in range(len(file_list2)):
        if not check_nonnegative_int(values3["startFrame" + str(i)]):
            resultString += "* Invalid Start frame " + str(i) + ".\n"
        else:
            if values3["endFrame" + str(i)] != "end" and (not check_nonnegative_int(values3["endFrame" + str(i)]) or
                     int(values3["endFrame" + str(i)]) < int(values3["startFrame" + str(i)])):
                resultString += "* Invalid End frame " + str(i) + ".\n"

    if resultString == "":
        resultString = "OK"

    return resultString


### Main starts here ###

sg.theme("Default1")

layout1 = [
            [sg.Text("Task list")],
            [sg.Listbox(values=[], enable_events=True, size=(100, 15), key="listBox1"),
             sg.Column([[sg.Button("+", size=(4,1))],
                        [sg.Button("-", size=(4,1))],
                        [sg.Button("Edit", size=(4,1))],
                        [sg.Button("Clear", size=(4,1))]])],
            [sg.Multiline(size=(100,10), disabled=True, key="textOutput")],
            [sg.Button("Run"), sg.Button("Close")]
        ]

window1 = sg.Window(title="Task list", layout=layout1, finalize=True)
task_name_list = []
all_tasks_dictionary = {}

while True:
    event1, values1 = window1.read(timeout=300)
    if event1 in [sg.WIN_CLOSED, "Close"]:
        break

    elif event1 == "Run":
        check1 = check_parameters1()
        if check1 == "OK":
            do_run()
            all_tasks_dictionary.clear()
            task_name_list=[]
        else:
            sg.popup("Input not correct:\n" + check1, title="Error!")

    elif event1 == "-":
        if len(values1["listBox1"]) > 0 and len(values1["listBox1"][0]) > 0:
            task_name_list.remove(values1["listBox1"][0])
            del all_tasks_dictionary[values1["listBox1"][0]]
            window1["listBox1"].update(task_name_list)

    elif event1 == "+":
        add_task();
        
    elif event1 == "Edit":
        if len(values1["listBox1"]) > 0 and len(values1["listBox1"][0]) > 0:
            try:
                edit_task(values1["listBox1"][0])
            except:
                edit_task(values1["listBox1"])
        
    elif event1 == "Clear":
        clear_task_list()
        all_tasks_dictionary.clear()
        task_name_list=[]


window1.close()

