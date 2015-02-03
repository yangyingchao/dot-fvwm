#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from os.path import walk
import sys
from copy import deepcopy


#################  Customized Variables #################
USER_HOME = os.getenv("HOME")
FVWM_HOME = os.path.join(USER_HOME, ".fvwm")

menu_template = "Menu_Template"
menu_template = os.path.join(FVWM_HOME, "tools", menu_template)
menu_template_head = menu_template + "_Head"
menu_template_tail = menu_template + "_Tail"

fvwm_icon_home = os.path.join(FVWM_HOME, "icons/apps")
fvwm_menu_output = os.path.join(FVWM_HOME, "Menu")

DESKTOP_SEARCH_PATH = ["/usr/share/applications",
                       os.path.join(USER_HOME, ".local/share/applications")]

class ImageCollection:
    def __init__(self, paths):
        self.img_data = {}
        for path in paths:
            if os.path.islink(path):
                path = os.path.abspath(path)
            os.path.walk(path, self._collect, None)
        print "Finished icon collection, size: ", len(self.img_data)

    def PrepareIcon(self, name, isCat=False):
        icon_fallback = ""
        if os.access(name, os.F_OK): # Input is the absloute path of file.
            icon_fallback = name;
        if isCat: # Categories start with applications-.
            name = name.lower()
            if "network" in name:
                name = "internet.png"
            elif "audiovideo" in name:
                name = "multimedia.png"
            name = "applications-%s"%name

        bname = os.path.basename(name)
        if "cxmenu-" in name:
            name = name[name.rfind("-")+1:]
        icon_path = ""
        pos = bname.rfind(".")
        if pos != -1:
            bname = bname[:pos]
        icon_path = self.img_data.get(bname.lower())

        if icon_path is None:
            icon_path = icon_fallback
        icon_out = ""
        if icon_path:
            pos = bname.rfind(".")
            if pos != -1:
                bname = bname[:pos] + ".png"
            else:
                bname += ".png"
            icon_out = os.path.join(fvwm_icon_home, bname)
            os.system('convert -background none -resize 24x24 "%s" "%s"'%(
                icon_path, icon_out))

        return icon_out

    def _collect(self, arg, dirname, filenames):
        #TODO: This should be optimized by analyzing "index.theme" file.
        size = len(filenames)
        for i in range(size):
            idx = size - 1 -i;
            fn = filenames[idx]
            if fn.find("16") != -1 or fn.find("22") != -1 or \
               fn.find("32") != -1 or fn.find("24") != -1 or \
               fn == "scalable":
                filenames.pop(idx);
                continue

            path = os.path.join(dirname, fn)
            if os.path.isdir(path):
                continue

            key = fn.split(".")[0].lower()
            self.img_data[key] = path

g_iconBase = ImageCollection(["/usr/share/pixmaps", "/usr/share/icons/hicolor",
                              os.path.join(USER_HOME, ".icons/default"),
                              os.path.join(USER_HOME, ".fvwm/icons/collection")])

def SimpleRead(fn):
    """
    read file and return content.
    Arguments:
    - `fn`:
    """
    content = ""
    try:
        content = open(fn).read()
    except :
        print("Failed to read file: %s\n"%(fn))
        print sys.exc_info()[1]

    return content


def SimpleWrite(fn, content):
    """

    Arguments:
    - `fn`:
    - `content`:
    """
    fd = None
    try:
        fd = open(fn, "w")
    except:
        print("Failed to open file: %s for writting\n"%(fn))
        print sys.exc_info()[1]
        return False
    else:
        fd.truncate(0)
        fd.write(content)
        fd.close()
        return True

def remove_if(lst, ele):
    while ele in lst:
        lst.remove(ele)

class DesktopEntry:
    """
    DesktopEntry representation.
    """

    def __init__(self, path):
        """
        """
        self.Category = None
        self.Name     = None
        self.Icon     = None
        self.Exec     = None

        # Optional
        self.terminal = False

        self.IsValid  = True
        self.InVisiable = True

        self._parse(path)

    def _parse(self, path):
        """
        """
        content = SimpleRead(path)
        if "Desktop Entry" not in content:
            self.IsValid = False
            return

        content = content.split("\n")
        tmp_dic = {}
        for item in content:
            kvp = item.split("=")
            if len(kvp) == 2:
                tmp_dic[kvp[0]] = kvp[1]

        self.InVisiable = tmp_dic.get("NoDisplay")
        if self.InVisiable:
            return

        self.Icon = tmp_dic.get("Icon")
        self.Name = tmp_dic.get("Name")
        self.Exec = tmp_dic.get("Exec")

        if self.Name is None or self.Exec is None:
            self.IsValid = False
            return
        elif self.Name in ["sandbox"]:
            self.InVisiable = True
            return

        if self.Exec.rfind("%") != -1:
            self.Exec = self.Exec[:self.Exec.rfind("%")]

        # Update self.Category if necessary
        self.Category = tmp_dic.get("Categories")
        self._updateCategory(tmp_dic.get("MimeType"))

    def _updateCategory(self, mimes):
        if self.Category is None:
            self.Category = "Other"

        if (mimes is not None) and ("audio" in mimes or "video" in mimes):
            self.Category = "AudioVideo"
        elif "Windows" in self.Name or "Microsoft" in self.Name or \
             "cxoffice" in self.Name or "cxmenu" in self.Category or \
             "cross"    in self.Name.lower():
            self.Category = "Wine"
        elif "Develop" in self.Category:
            self.Category = "Development"
        elif "Setting" in self.Category:
            self.Category = "System"
        elif "Office" in self.Category:
            self.Category = "Office"
        elif "Utility" in self.Category:
            self.Category = "utilities"
        elif "Network" in self.Category:
            self.Category = "network"
        elif "System" in self.Category:
            self.Category = "system"
        else:
            self.Category = self.Category.split(";")[0]


    def SerializeToString(self):
        """
        It will do two things:
        1. Find icon and convert to proper size.
        2. Return a string which can be inserted into fvwm menu.
        """

        icon_out = g_iconBase.PrepareIcon(self.Icon)
        return '+ "%%%s%%%s" Exec exec %s\n'%(icon_out, self.Name,
                                              self.Exec)

class DE_Category:
    """
    """
    def __init__(self, name):
        """
        """
        self.Name = name
        self.Icon = name + ".png"
        self.DEs=set()
        print "Createing CAT: ", name
        pass

    def StoreEntry(self, de):
        self.DEs.add(de)

    def SerializeToString(self):
        """ Returns a tuple.
        First part is the entry to be added to MenuFvwmRoot.
        Second part is menu definition of this category.
        """
        print "Called for: ", self.Name, "Len: ", len(self.DEs)
        icon_out = g_iconBase.PrepareIcon(self.Icon, True)
        first = '+ "%%%s%%%s" Popup Menu%s\n'%(icon_out, self.Name, self.Name)
        second = "\nDestroyMenu Menu%s\nAddToMenu Menu%s\n"%(self.Name, self.Name)
        for de in self.DEs:
            second += de.SerializeToString()
        second += "\n\n"
        return (first, second)

class FvwmMenuFactory:
    def __init__(self):
        self.cats = {}
        pass

    def Feed(self, path):
        """Feed and parse path, generate DE and store it.

        Arguments:
        - `path`:
        """
        de = DesktopEntry(path)
        if not de.IsValid:
            print("File %s path is not valid!\n"%path)
            return
        if de.InVisiable:
            print("File :%s is invisible.\n"%path)
            return


        cat = self.cats.get(de.Category)
        if cat is None:
            cat = DE_Category(de.Category)
            self.cats[de.Category] = cat
        self.cats[de.Category].StoreEntry(de)

    def OutputToFile(self, of=os.path.join(FVWM_HOME, "Menu")):
        output   = SimpleRead(menu_template_head)
        submenus = []
        for cat in self.cats.values():
            content = cat.SerializeToString()
            output += content[0]
            submenus.append(content[1])

        output += SimpleRead(menu_template_tail)

        for sm in submenus:
            output += sm + "\n"
        SimpleWrite(of, output)

def process_desktop_entries(menu, dirname, filenames):
    """
    Parse each file in this subdir, store information into fvwm_menu;
    """
    for filename in filenames:
        path = os.path.join(dirname, filename)
        if os.path.isdir(path) or not path.endswith("desktop"):
            continue
        else:
            menu.Feed(path)

if __name__ == '__main__':

    menu = FvwmMenuFactory()

    print ("Searching and analyzing desktop entries...")
    for item in DESKTOP_SEARCH_PATH:
        os.path.walk(item, process_desktop_entries, menu)
    print ("Finished analyze desktop entries.\n")
    menu.OutputToFile()
