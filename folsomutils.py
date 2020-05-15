# Folsom Utils
# Version: 2020.05.15
#

import argparse
import datetime
import glob
import os
import pprint
import shutil
import sys
import time
import traceback
import json
import jsonpickle
import inspect
from enum import Enum

#=====================================================================================
# Configuration
#-------------------------------------------------------------------------------------

# Less frequent configurations
INDENT = 4


#=====================================================================================
# Global variables
#-------------------------------------------------------------------------------------
pp = pprint.PrettyPrinter(indent=INDENT, width=120)
indent = ""
waitcounter = 0

#=====================================================================================
# LOGGING FUNCTIONS AND INTERACTIVE FUNCTIONS
#-------------------------------------------------------------------------------------

RED = "\033[01;31m"
GREEN = "\033[01;32m"
YELLOW = "\033[01;33m"
BLUE = "\033[01;34m"
PURPLE = "\033[01;35m"
WHITE = "\033[01;37m"

BDRED = "\033[1;91m"
BDBLACK = "\033[01;38m"

BGBLACK = "\033[01;40m"
BGRED = "\033[01;41m"
BGGREEN = "\033[01;42m"
BGYELLOW = "\033[01;43m"
BGBLUE = "\033[01;44m"

RESET = "\033[0m"  # Text Reset


def log(s):
    print(indent + s, file=sys.stdout, flush=True)

def logc(s, color):
    print(indent + color + s + RESET, file=sys.stdout, flush=True)

def logError(s, reverse=False):
    if reverse:
        print(indent + BGRED + s + RESET, file=sys.stdout, flush=True)
    else:
        print(indent + BDRED + s + RESET, file=sys.stdout, flush=True)

def logWarning(s, reverse=False):
    if reverse:
        print(indent + BGYELLOW + s + RESET, file=sys.stdout, flush=True)
    else:
        print(indent + YELLOW + s + RESET, file=sys.stdout, flush=True)

def logSuccess(s, reverse=False):
    if reverse:
        print(indent + BGGREEN + s + RESET, file=sys.stdout, flush=True)
    else:
        print(indent + GREEN + s + RESET, file=sys.stdout, flush=True)

def logInfo(s, reverse=False):
    if reverse:
        print(indent + BGBLUE + s + RESET, file=sys.stdout, flush=True)
    else:
        print(indent + BLUE + s + RESET, file=sys.stdout, flush=True)

def logWithTimestamp(s):
    print(indent + str(datetime.datetime.now()) + " | " + s, file=sys.stdout, 
            flush=True)

def logg(s):
    print(s, end="", file=sys.stdout, flush=True)

def logPrettyStr(name, var):
    print(indent + name + " = " + var, file=sys.stdout, flush=True)

def logPretty(name, var):
    if type(var) is str:
        return logPrettyStr(name, var)
    print(indent + name + " = ")
    fstring = indent + '{}'
    print(''.join([fstring.format(l) for l in pp.pformat(var).splitlines(True)]))
    sys.stdout.flush()

def logTime():
    currentTime = datetime.datetime.today()
    dateStr = currentTime.strftime("%Y-%m-%d %H:%M:%S")
    log("Current Time: %s." %(dateStr))

def logLine():
    log("-----------------------------------------------------------------------------------------")

def logLLine():
    log("=========================================================================================")

def secsToStr(secs):
    if secs < 0:
        return '---'
    hour = secs // 3600
    secs = secs % 3600
    minutes = secs // 60
    secs = secs % 60
    output = ""
    if hour > 0:
        output = "%s hrs " % hour
    if minutes > 0:
        output = "%s%s mins " %(output, minutes)
    output = "%s%s secs" %(output, secs)
    return output

def logStats(startTime, initialDoneCount, processedCount, doneCount, totalCount):
    currentTime = datetime.datetime.today()
    elapsedTimeSecs = (currentTime - startTime).seconds
    remainingCount = totalCount - doneCount
    doneInCurrentSession = doneCount - initialDoneCount
    remainingTimeSecs = -1
    if doneInCurrentSession > 0:
        remainingTimeSecs = int(remainingCount * elapsedTimeSecs / doneInCurrentSession)
    dateStr = currentTime.strftime("%Y-%m-%d %H:%M:%S")
    log("Processed          : %s/%s" %(str(processedCount), str(totalCount)))
    log("Complete           : %s/%s" %(str(doneCount), str(totalCount)))
    log("Current Time       : %s" %(dateStr))
    log("Elapsed Duration   : %s" %(secsToStr(elapsedTimeSecs)))
    log("Remaining Duration : %s" %(secsToStr(remainingTimeSecs)))

def increaseIndent():
    global indent
    indent = indent + ' ' * INDENT

def decreaseIndent():
    global indent
    if len(indent) >= INDENT:
        indent = indent[:-INDENT]
    else:
        indent = 0

def countdown(n, successMsg):
    if n <= 0:
        return
    for counter in range(n, 0, -1):
        logg("\rWaiting " + str(counter) + ' seconds... ')
        time.sleep(1)
    log("\r" + successMsg + "                ")

def wait(n):
    global waitcounter
    if n <= 0:
        return
    waitchars = ['-', '\\', '|', '/']
    for counter in range(0, n * 10):
        waitcounter = waitcounter + 1
        index = waitcounter % len(waitchars)
        logg("\r%s" %(waitchars[index]))
        time.sleep(0.10)
    logg("\r                ")
    logg("\r")

#=====================================================================================
def loadSymbolList(filename):
    f = open(filename, "r")
    lines = f.readlines()
    f.close()

    symbols = []
    for line in lines:
        line2 = line.strip()
        if line2 != "":
            symbols.append(line2)
    return symbols

#=====================================================================================
def savesymbolList(symbols, filename):
    filename = filename.replace(": ", "-");
    filename = filename.replace(":", "-");
    f = open(filename, "w")
    for item in symbols:
        f.write("%s\n" % item)
    f.close()

#=====================================================================================
class ObjectEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, "to_json"):
            return self.default(obj.to_json())
        elif hasattr(obj, "__dict__"):
            d = dict(
                (key, value)
                for key, value in inspect.getmembers(obj)
                if not key.startswith("__")
                and not inspect.isabstract(value)
                and not inspect.isbuiltin(value)
                and not inspect.isfunction(value)
                and not inspect.isgenerator(value)
                and not inspect.isgeneratorfunction(value)
                and not inspect.ismethod(value)
                and not inspect.ismethoddescriptor(value)
                and not inspect.isroutine(value)
            )
            return self.default(d)
        return obj

def saveJson(obj, filename):
    #jsonpickle.set_encoder_options('json', indent=4)
    #jsonpickle.set_encoder_options('simplejson', indent=4)
    #s = jsonpickle.encode(obj, unpicklable=False)
    #s = json.dumps(obj, , sort_keys=True, indent=4)
    #s = ObjectEncoder().encode(obj, sort_keys=True, indent=4)
    s = json.dumps(obj, cls=ObjectEncoder, sort_keys=True, indent=4)
    f = open(filename, "w")
    f.write("%s" % s)
    f.close()

#=====================================================================================
def loadJson(filename):
    with open(filename) as json_data:
        d = json.load(json_data)
        return d
    return None
