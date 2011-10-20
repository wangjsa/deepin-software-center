#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 Deepin, Inc.
#               2011 Yong Wang
# 
# Author:     Yong Wang <lazycat.manatee@gmail.com>
# Maintainer: Yong Wang <lazycat.manatee@gmail.com>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from constant import *
from math import pi
import cairo
import gtk
import hashlib
import locale
import math
import os
import pango
import pangocairo
import pygtk
import stat
import subprocess
import threading as td
import time
import uuid
pygtk.require('2.0')

def isDoubleClick(event):
    '''Whether an event is double click?'''
    return event.button == 1 and event.type == gtk.gdk._2BUTTON_PRESS

def getStarPath(starIndex, starLevel):
    '''Get star path.'''
    if starIndex == 1:
        if starLevel > 8:
            imgPath = "star_green.png"
        elif starLevel > 2:
            imgPath = "star_yellow.png"
        elif starLevel == 2:
            imgPath = "star_red.png"
        else:
            imgPath = "halfstar_red.png"
    elif starIndex in [2, 3, 4]:
        if starLevel > 8:
            imgPath = "star_green.png"
        elif starLevel >= starIndex * 2:
            imgPath = "star_yellow.png"
        elif starLevel == starIndex * 2 - 1:
            imgPath = "halfstar_yellow.png"
        else:
            imgPath = "star_gray.png"
    elif starIndex == 5:
        if starLevel >= starIndex * 2:
            imgPath = "star_green.png"
        elif starLevel == starIndex * 2 - 1:
            imgPath = "halfstar_green.png"
        else:
            imgPath = "star_gray.png"
            
    return "cell/%s" % (imgPath)

def getFontFamilies():
    '''Get all font families in system.'''
    fontmap = pangocairo.cairo_font_map_get_default()
    return map (lambda f: f.get_name(), fontmap.list_families())

def getScreenSize(widget):
    '''Get widget's screen size.'''
    screen = widget.get_screen()
    width = screen.get_width()
    height = screen.get_height()
    return (width, height)

def getPkgIcon(pkg, iconWidth=32, iconHeight=32):
    '''Get package icon.'''
    iconPath = "../pkgData/AppIcon/" + pkg.name + ".png"
    if os.path.exists (iconPath):
        return gtk.image_new_from_pixbuf(gtk.gdk.pixbuf_new_from_file_at_size(iconPath, iconWidth, iconHeight))
    else:
        return gtk.image_new_from_pixbuf(gtk.gdk.pixbuf_new_from_file_at_size("../theme/default/icon/appIcon.ico", 
                                                                              iconWidth, iconHeight))
def getPkgName(pkg):
    '''Get package name.'''
    return pkg.name

def getPkgExecPath(pkg):
    '''Get path of execute file.'''
    execPath = "../pkgData/pkgPath/%s" % (pkg.name)
    if os.path.exists(execPath):
        execFile = open(execPath, "r")
        content = execFile.read()
        execFile.close()
        
        return content
    else:
        return None

def evalFile(filepath):
    '''Eval file content.'''
    readFile = open(filepath, "r")
    content = eval(readFile.read())
    readFile.close()
    
    return content

def writeFile(filepath, content):
    '''Write file.'''
    f = open(filepath, "w")
    f.write(content)
    f.close()

def getPkgShortDesc(pkg):
    '''Get package's short description.'''
    pkgPath = "../pkgData/pkgInfo/" + pkg.name
    if os.path.exists(pkgPath):
        lang = getDefaultLanguage()
        if lang == "zh_CN":
            return ((evalFile(pkgPath))["zh-CN"])["shortDesc"]
        elif lang == "zh_TW":
            return ((evalFile(pkgPath))["zh-TW"])["shortDesc"]
        # Default use English.
        else:
            return ((evalFile(pkgPath))["en"])["shortDesc"]
            
    else:
        return pkg.candidate.summary

def getPkgLongDesc(pkg):
    '''Get package's long description.'''
    pkgPath = "../pkgData/pkgInfo/" + pkg.name
    if os.path.exists(pkgPath):
        lang = getDefaultLanguage()
        if lang == "zh_CN":
            return ((evalFile(pkgPath))["zh-CN"])["longDesc"]
        elif lang == "zh_TW":
            return ((evalFile(pkgPath))["zh-TW"])["longDesc"]
        # Default use English.
        else:
            return ((evalFile(pkgPath))["en"])["longDesc"]
            
    else:
        return pkg.candidate.description

def getPkgVersion(pkg):
    '''Get package's version.'''
    # Return current version if package has installed. 
    if pkg.is_installed:
        return pkg.installed.version    
    # Otherwise return candidate version.
    else:
        return pkg.candidate.version

def getPkgNewestVersion(pkg):
    '''Get package's newest version.'''
    if len(pkg.versions) == 0:
        print "%s: length of pkg.versions equal 0." % (getPkgName(pkg))
        return pkg.candidate.version
    else:
        return pkg.versions[0].version

def getPkgSection(pkg):
    '''Get package's section.'''
    return pkg.candidate.section

def getPkgSize(pkg):
    '''Get package's  size.'''
    return pkg.candidate.size

def getPkgHomepage(pkg):
    '''Get homepage of package.'''
    return pkg.candidate.homepage

def getPkgInstalledSize(pkg):
    '''Get package's installed size.'''
    return pkg.candidate.installed_size

def getPkgDependSize(cache, pkg, action):
    '''Get package's dependent size.'''
    try:
        # Clear first.
        cache.clear()
        
        # Mark package.
        if action == ACTION_INSTALL:
            pkg.mark_install()
        elif action == ACTION_UPGRADE:
            pkg.mark_upgrade()
        else:
            pkg.mark_delete()
            
        # Get change size.
        cache.get_changes()
        downloadSize = cache.required_download
        useSize = abs(cache.required_space)
        
        # Clear last.
        cache.clear()
        
        return (downloadSize, useSize)
    except Exception, e:
        # Just return package's size if exception throwed.
        print "Calculate `%s` dependent used size failed, instead package's used size." % (getPkgName(pkg))
        return (pkg.candidate.size, pkg.candidate.installed_size)

def getCommandOutputFirstLine(commands):
    '''Run command and return result.'''
    process = subprocess.Popen(commands, stdout=subprocess.PIPE)
    process.wait()
    return process.stdout.readline()

def getCommandOutput(commands):
    '''Run command and return result.'''
    process = subprocess.Popen(commands, stdout=subprocess.PIPE)
    process.wait()
    return process.stdout.readlines()
    
def getKernelPackages():
    '''Get running kernel packages.'''
    kernelVersion = (getCommandOutputFirstLine(["uname", "-r"]).split("-generic"))
    
    return ["linux-image-generic", 
            "linux-image-%s-generic" % (kernelVersion),
            "linux-headers-generic", 
            "linux-headers-%s" % (kernelVersion),
            "linux-headers-%s-generic" % (kernelVersion),
            "linux-generic"
            ]

KERNEL_PACKAGES = getKernelPackages()    
    
def isPkgUninstallable(pkg, checkInstalled=True):
    '''Is pkg is un-installable?'''
    inFilterSection = pkg.candidate.section in ["libs", "libdevel", "oldlibs"]
    isKernelPackages = pkg.name in KERNEL_PACKAGES
    
    # When first use cache need check installed.
    if checkInstalled:
        return pkg.is_installed and not pkg.essential and not inFilterSection and not isKernelPackages
    # Don't need check installed status when running.
    # Because package's is_installed not update sometimes.
    else:
        return not pkg.essential and not inFilterSection and not isKernelPackages

def containerRemoveAll(container):
    '''Remove all child widgets from container.'''
    container.foreach(lambda widget: container.remove(widget))

def formatFileSize(bytes, precision=2):
    '''Returns a humanized string for a given amount of bytes'''
    bytes = int(bytes)
    if bytes is 0:
        return '0B'
    else:
        log = math.floor(math.log(bytes, 1024))
        quotient = 1024 ** log
        size = bytes / quotient
        remainder = bytes % quotient
        if remainder < 10 ** (-precision): 
            prec = 0
        else:
            prec = precision
        return "%.*f%s" % (prec,
                           size,
                           ['B', 'KB', 'MB', 'GB', 'TB','PB', 'EB', 'ZB', 'YB']
                           [int(log)])

def pixbufNewFromIcon(stockId, size):
    '''Create pixbuf from given id and size.'''
    iconTheme = gtk.icon_theme_get_for_screen(gtk.gdk.screen_get_default())
    return iconTheme.load_icon(stockId, size, gtk.ICON_LOOKUP_USE_BUILTIN)

def isInRect((cx, cy), (x, y, w, h)):
    '''Whether coordinate in rectangle.'''
    return (cx >= x and cx <= x + w and cy >= y and cy <= y + h)

def scrollToTop(scrolledWindow):
    '''Scroll scrolled window to top.'''
    scrolledWindow.get_vadjustment().set_value(0)
    
def postGUI(func):
    '''Post GUI code in main thread.'''
    def wrap(*a, **kw):
        gtk.gdk.threads_enter()
        ret = func(*a, **kw)
        gtk.gdk.threads_leave()
        return ret
    return wrap

def printExecTime(func):
    '''Print execute time.'''
    def wrap(*a, **kw):
        startTime = time.time()
        ret = func(*a, **kw)
        print "%s time: %s" % (str(func), time.time() - startTime)
        return ret
    return wrap

def printEnv():
    '''Print environment variable.'''
    for param in os.environ.keys():
        print "*** %20s %s" % (param,os.environ[param])                

def setProgress(progressbar, progress):
    '''Set progress.'''
    progressbar.set_fraction(progress / 100.0)
    if progress == 0:
        progressbar.set_text("")
    else:
        progressbar.set_text(str(progress) + "%")

def resizeWindow(widget, event, window):
    '''Re-size window.'''
    # If a shift key is pressed, start resizing
    if event.state & gtk.gdk.SHIFT_MASK:
        window.begin_resize_drag(
            gtk.gdk.WINDOW_EDGE_SOUTH_EAST, 
            event.button, 
            int(event.x_root), 
            int(event.y_root), 
            event.time)
    
def moveWindow(widget, event, window):
    '''Move window.'''
    window.begin_move_drag(
        event.button, 
        int(event.x_root), 
        int(event.y_root), 
        event.time)

def addInScrolledWindow(scrolledWindow, widget, shadowType=gtk.SHADOW_NONE):
    '''Like add_with_viewport in ScrolledWindow, with shadow type.'''
    scrolledWindow.add_with_viewport(widget)
    viewport = scrolledWindow.get_child()
    if viewport != None:
        viewport.set_shadow_type(shadowType)
    else:
        print "addInScrolledWindow: Impossible, no viewport widget in ScrolledWindow!"
    
def newButtonWithoutPadding(content=None):
    '''Create button without padding.'''
    button = gtk.Button(content)
    button.set_property("can-focus", False)
    return button

def getFontYCoordinate(y, height, fontSize):
    '''Get font y coordinate.'''
    return y + (height + fontSize) / 2 - 1

# This is a hacking way, 
# Author recommend use xmlrpclib.ServerProxy('http://localhost:6800/rpc').getVersion() get version number.
# But above solution easy to failed when connect is unavailable.
# So i pick version information from output of command "aria2c --version".
def getAria2Version():
    '''Get aria2 version.'''
    versionList = getCommandOutputFirstLine(["aria2c", "--version"]).split().pop().split('.')
    
    return (int(versionList[0]), int(versionList[1]), int(versionList[2]))

def getCandidates(pkgs, text):
    '''Get candidates.'''
    if len(text) == 0:
        return []
    else:
        # Filter match candidates.
        candidates = []
        for pkg in pkgs:
            if text in pkg:
                (preStr, matchStr, restStr) = pkg.partition(text)
                candidates.append((preStr, matchStr, restStr, pkg))
                
        return map(lambda (preStr, matchStr, restStr, pkg): 
                   # Highlight keyword.
                   [preStr + "<span foreground='#1A3E88'><b>" + matchStr + "</b></span>" + restStr, pkg],
                   # Sorted candidates.
                   sorted(candidates, cmp=compareCandidates))
    
def compareCandidates((preA, matchA, restA, pkgA), (preB, matchB, restB, pkgB)):
    '''Compare candidates.'''
    lenA = len(preA)
    lenB = len(preB)
    # Candidate's order at front if pre string's length shorter.
    if lenA < lenB:
        return -1
    # Compare package name if pre string's length is same.
    elif lenA == lenB:
        return cmp(pkgA, pkgB)
    else:
        return 1        

def getCurrentTime():
    '''Get current time.'''
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

def setClickableCursor(widget):
    '''Set click-able cursor.'''
    # Use widget in lambda, and not widget pass in function.
    # Otherwise, if widget free before callback, you will got error:
    # free variable referenced before assignment in enclosing scope, 
    widget.connect("enter-notify-event", lambda w, e: setCursor(w, gtk.gdk.HAND2))
    widget.connect("leave-notify-event", lambda w, e: setDefaultCursor(w))
        
def setCursor(widget, cursorType):
    '''Set cursor.'''
    widget.window.set_cursor(gtk.gdk.Cursor(cursorType))
    
    return False

def setDefaultCursor(widget):
    '''Set default cursor.'''
    widget.window.set_cursor(None)
    
    return False

def setLabelMarkup(widget, label, normalMarkup, activeMarkup):
    '''Set label markup.'''
    widget.connect("enter-notify-event", lambda w, e: setMarkup(label, activeMarkup))
    widget.connect("leave-notify-event", lambda w, e: setMarkup(label, normalMarkup))
    
def setMarkup(label, markup):
    '''Set markup.'''
    label.set_markup(markup)
    
    return False

def setDefaultToggleLabel(content, status, setStatus, getStatus, selectDefault=True):
    '''Set default toggle label, return label and eventbox.'''
    normalColor = '#1A3E88'
    hoverColor = '#0084FF'
    selectColor = '#000000'
    
    label = gtk.Label()
    eventbox = gtk.EventBox()
    if selectDefault:
        initMarkup = "<span foreground='%s' size='%s' underline='single'>%s</span>" % (selectColor, LABEL_FONT_SIZE, content)
    else:
        initMarkup = "<span foreground='%s' size='%s'>%s</span>" % (normalColor, LABEL_FONT_SIZE, content)
    setToggleLabel(
        eventbox,
        label,
        initMarkup,
        "<span foreground='%s' size='%s' >%s</span>" % (normalColor, LABEL_FONT_SIZE, content),
        "<span foreground='%s' size='%s' >%s</span>" % (hoverColor, LABEL_FONT_SIZE, content),
        "<span foreground='%s' size='%s' underline='single'>%s</span>" % (selectColor, LABEL_FONT_SIZE, content),
        status,
        setStatus,
        getStatus
        )
    
    return (label, eventbox)

def setToggleLabel(widget, label, initMarkup, normalMarkup, hoverMarkup, selectMarkup, labelId, setLabelId, getCurrentId):
    '''Set toggle label.'''
    # Init.
    widget.set_visible_window(False)
    widget.add(label)
    label.set_markup(initMarkup)
    
    # Set label id.
    widget.connect("button-press-event", lambda w, e: setLabelId(labelId))
    
    # Set label markup.
    widget.connect("enter-notify-event", 
                   lambda w, e: setLabelEntryMarkup(label, hoverMarkup, selectMarkup, labelId, getCurrentId))
    widget.connect("leave-notify-event", 
                   lambda w, e: setLabelLeaveMarkup(label, normalMarkup, selectMarkup, labelId, getCurrentId))
    
    # Set label cursor.
    widget.connect("enter-notify-event", lambda w, e: setCursor(w, gtk.gdk.HAND2))
    widget.connect("leave-notify-event", lambda w, e: setDefaultCursor(w))
    
def setLabelEntryMarkup(label, hoverMarkup, selectMarkup, labelId, getCurrentId):
    '''Set label markup color.'''
    if labelId == getCurrentId():
        setMarkup(label, selectMarkup)
    else:
        setMarkup(label, hoverMarkup)    
        
def setLabelLeaveMarkup(label, normalMarkup, selectMarkup, labelId, getCurrentId):
    '''Set label markup color.'''
    if labelId == getCurrentId():
        setMarkup(label, selectMarkup)
    else:
        setMarkup(label, normalMarkup)    

def setDefaultClickableLabel(content, normalColor="#1A3E88", hoverColor="#0084FF", size=LABEL_FONT_SIZE, resetAfterClick=True):
    '''Create clickable label and return label and eventbox.'''
    # Init.
    label = gtk.Label()
    label.set_markup(
        "<span foreground='%s' size='%s'>%s</span>" % (normalColor, size, content))
    eventbox = gtk.EventBox()
    eventbox.set_visible_window(False)
    eventbox.add(label)
    setClickableLabel(
        eventbox,
        label,
        "<span foreground='%s' size='%s'>%s</span>" % (normalColor, size, content),
        "<span foreground='%s' size='%s'>%s</span>" % (hoverColor, size, content),
        resetAfterClick
        )
    
    return (label, eventbox)
        
def setClickableLabel(widget, label, normalMarkup, activeMarkup, resetAfterClick=True):
    '''Set click-able label.'''
    # Set label markup.
    widget.connect("enter-notify-event", lambda w, e: setMarkup(label, activeMarkup))
    widget.connect("leave-notify-event", lambda w, e: setMarkup(label, normalMarkup))
    
    # Set label cursor.
    widget.connect("enter-notify-event", lambda w, e: setCursor(w, gtk.gdk.HAND2))
    widget.connect("leave-notify-event", lambda w, e: setDefaultCursor(w))
    
    # Reset color when click widget.
    if resetAfterClick:
        widget.connect("button-press-event", lambda w, e: setMarkup(label, normalMarkup))

def setCustomizeClickableCursor(eventbox, widget, cursorDPixbuf):
    '''Set click-able cursor.'''
    eventbox.connect("enter-notify-event", lambda w, e: setCustomizeCursor(widget, cursorDPixbuf))
    eventbox.connect("leave-notify-event", lambda w, e: setDefaultCursor(widget))
        
def setCustomizeCursor(widget, cursorDPixbuf):
    '''Set cursor.'''
    widget.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.display_get_default(),
                                            cursorDPixbuf.getPixbuf(),
                                            0, 0))
    return False
    
def runCommand(command):
    '''Run command.'''
    subprocess.Popen("nohup %s > /dev/null 2>&1" % (command), shell=True)
    
def touchFile(filepath):
    '''Touch file.'''
    # Create directory first.
    dir = os.path.dirname(filepath)
    if not os.path.exists(dir):
        os.makedirs(dir)
        
    # Touch file.
    open(filepath, "w").close()

def getDefaultLanguage():
    '''Get default language.'''
    (lang, _) = locale.getdefaultlocale()
    return lang

def setHelpTooltip(widget, helpText):
    '''Set help tooltip.'''
    widget.connect("enter-notify-event", lambda w, e: showHelpTooltip(w, helpText))

def showHelpTooltip(widget, helpText):
    '''Create help tooltip.'''
    widget.set_has_tooltip(True)
    widget.set_tooltip_text(helpText)
    widget.trigger_tooltip_query()
    
    return False

def treeViewGetToplevelNodeCount(treeview):
    '''Get toplevel node count.'''
    model = treeview.get_model()
    if model != None:
        return model.iter_n_children(None)
    else:
        return 0
    
def treeViewGetSelectedPath(treeview):
    '''Get selected path.'''
    selection = treeview.get_selection()
    (_, treePaths) = selection.get_selected_rows()
    if len(treePaths) != 0:
        return (treePaths[0])[0]
    else:
        return None
 
def treeViewFocusFirstToplevelNode(treeview):
    '''Focus first toplevel node.'''
    treeview.set_cursor((0))
    
def treeViewFocusLastToplevelNode(treeview):
    '''Focus last toplevel node.'''
    nodeCount = treeViewGetToplevelNodeCount(treeview)
    if nodeCount > 0:
        path = (nodeCount - 1)
    else:
        path = (0)
    treeview.set_cursor(path)

def treeViewFocusNextToplevelNode(treeview):
    '''Focus next toplevel node.'''
    selectedPath = treeViewGetSelectedPath(treeview)
    if selectedPath != None:
        nodeCount = treeViewGetToplevelNodeCount(treeview)
        if selectedPath < nodeCount - 1:
            treeview.set_cursor((selectedPath + 1))

def treeViewFocusPrevToplevelNode(treeview):
    '''Focus previous toplevel node.'''
    selectedPath = treeViewGetSelectedPath(treeview)
    if selectedPath != None:
        if selectedPath > 0:
            treeview.set_cursor((selectedPath - 1))

def removeFile(path):
    '''Remove file.'''
    if os.path.exists(path):
        print "Remove ", path
        os.remove(path)

def getUserID():
    '''Get Mac Address and MD5.'''
    macAddress = uuid.getnode()
    return (hashlib.md5(str(macAddress))).hexdigest()

def getLastUpdateHours(filepath):
    """
    Return the number of hours since last update.
    
    If the date is unknown, return "None"
    """
    if not os.path.exists(filepath):
        return None
    agoHours = int((time.time() - os.stat(filepath)[stat.ST_MTIME]) / (60 * 60))
    return agoHours

class AnonymityThread(td.Thread):
    '''Anonymity thread.'''

    def __init__(self, callback):
        '''Init anonymity thread.'''
        td.Thread.__init__(self)
        self.setDaemon(True) # make thread exit when main program exit

        self.callback = callback
        
    def run(self):
        '''Run.'''
        self.callback()    
        
def addInList(eList, element):
    '''Add element in list.'''
    if not element in eList:
        eList.append(element)
        
def removeFromList(eList, element):
    '''Remove element from list.'''
    if element in eList:
        eList.remove(element)
        
def sortAlpha(eList):
    '''Get alpha list.'''
    return sorted(eList, key=lambda e: e)

def todayStr():
    '''Get string of today.'''
    structTime = time.localtime()
    return "%s-%s-%s" % (structTime.tm_year, structTime.tm_mon, structTime.tm_mday)

def aptsearch(keywords):
    '''Search keywords.'''
    lines = getCommandOutput(["apt-cache", "search"] + keywords)
    pkgs = []
    for line in lines:
        splitList = line.split()
        if len(splitList) > 0:
            pkgs.append(splitList[0])        
            
    return pkgs

#  LocalWords:  halfstar AppIcon pkgInfo shortDesc zh TW longDesc downloadSize
#  LocalWords:  getPkgInstalledSize getPkgDependSize useSize uname libdevel ZB
#  LocalWords:  oldlibs resize moveWindow addInScrolledWindow scrolledWindow
#  LocalWords:  shadowType viewport newButtonWithoutPadding getFontYCoordinate
#  LocalWords:  fontSize xmlrpclib ServerProxy getVersion getAria versionList
#  LocalWords:  getCommandOutputFirstLine getCandidates pkgs len preStr matchStr restStr
#  LocalWords:  BBBB setMarkup activeMarkup normalMarkup setCursor eventbox
#  LocalWords:  setDefaultCursor resetAfterClick setCustomizeClickableCursor
#  LocalWords:  cursorPath setCustomizeCursor runCommand subprocess touchFile
#  LocalWords:  filepath makedirs getDefaultLanguage lang getdefaultlocale iter
#  LocalWords:  setHelpTooltip helpText showHelpTooltip treeview toplevel
#  LocalWords:  treeViewGetToplevelNodeCount treeViewGetSelectedPath treePaths
#  LocalWords:  treeViewFocusFirstToplevelNode treeViewFocusLastToplevelNode
#  LocalWords:  nodeCount treeViewFocusNextToplevelNode selectedPath removeFile
#  LocalWords:  treeViewFocusPrevToplevelNode
