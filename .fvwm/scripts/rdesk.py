#!/usr/bin/env python
# -*- coding: utf-8 -*-

######################################################################
## Yangyingchao@gmail 011 all rights reserved.
## Filename:    rdesk.py
## Description:
## Update:
## Date         Name            Reason
## ========== ================= =====================================
## 2011-10-25   Yang, Ying-chao Create
##
## Known issues:
##
## TODO:
##     1. Add or delete desktop configuration.
##     2. Encrypt stored passwords.
#####################################################################


import sys
import os
import wx
from threading import *
from subprocess import *
from ConfigParser import ConfigParser
from copy import deepcopy


APP="rdesktop"
TARGETS = []

t1 = { };
t1["ip"] = "10.190.40.62"
t1["username"] = "administrator"
t1["passwd"]  = "itcss2-1"

TARGETS.append(t1)

BTN_ID_Base = 10000;

global config

class Remote_Thread(Thread):
    def __init__(self, target):
        Thread.__init__(self)
        self.target = target
        self.p = None
        self.ret = 0

    def run(self):
        cmd = "%s -x l -r disk:diskname=/tmp -r clipboard:PRIMARYCLIPBOARD \
 -z -g %s -u %s -p %s %s"%\
            (config.configs["APP"], config.configs["GEO"],
             self.target["username"], self.target["password"],
             self.target["ip"])
        print cmd
        self.p = Popen(cmd, shell=True)
        sts = os.waitpid(self.p.pid, 0)
        self.ret = sts[1]

    def stop(self):
        self.p.kill()


class Frame(wx.Frame):
    def __init__(self, cfg):
        wx.Frame.__init__(self, None, -1, "RemotePC")
        self.buttons=[]
        self.r_thread = {}
        self.cfg = cfg
        vbox = wx.BoxSizer(wx.VERTICAL)

        idx = BTN_ID_Base
        tgs = self.cfg.configs.get("PCs")
        if tgs is None:
            return

        # hbox = wx.BoxSizer(wx.HORIZONTAL)
        # btn_quit = wx.Button(self, -1, "Quit")
        # hbox.Add(btn_quit, False, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER, 5)
        # btn_quit.Bind(wx.EVT_BUTTON, self.btn_quit_pressed)
        # btn_new =  wx.Button(self, -1, "New")
        # btn_new.Bind(wx.EVT_BUTTON, self.btn_new_pressed)
        # hbox.Add(btn_new, False, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER, 5)

        # vbox.Add(hbox, False, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER, 5)

        for item in tgs:
            hbox = wx.BoxSizer(wx.HORIZONTAL)
            hbox.Add(wx.StaticText(self, -1, "%d. "%(idx-BTN_ID_Base+1)),
                     False, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER, 5)

            hbox.Add(wx.StaticText(self, -1, item["ip"]),
                     True, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER, 5)

            btn = wx.ToggleButton(self, idx, "Connect")
            self.Bind(wx.EVT_TOGGLEBUTTON, self.btn_clicked)
            self.buttons.append(btn)
            hbox.Add(btn, False, wx.ALL|wx.EXPAND)

            vbox.Add(hbox, False, wx.ALL|wx.EXPAND)
            idx += 1

        # self.SetSizer(vbox)
        self.SetSizerAndFit(vbox)

        self.Show(True)

    def btn_quit_pressed(self, evt):
        """

        Arguments:
        - `evt`:
        """
        sys.exit(0)

    def btn_new_pressed(self, evt):
        pass

    def btn_clicked(self, evt):
        idx = evt.GetId() - BTN_ID_Base
        btn = self.buttons[idx]
        tg = self.cfg.configs["PCs"][idx]
        ip = tg.get("ip")
        if btn.GetValue():
            if self.r_thread.get(ip) is None:
                runner = Remote_Thread(tg)
                self.r_thread[tg["ip"]] = runner
            else:
                runner = self.r_thread.get(ip)

            runner.start()
            btn.SetLabel("Disconnect")
        else:
            if self.r_thread.get(ip) is None:
                print "%s not connected!"%ip
            else:
                runner = self.r_thread.get(ip)
                runner.stop()
                self.r_thread[ip] = None
            btn.SetLabel("Connect")


class RD_Config:
    def __init__(self):
        print "AA"
        self.parser = ConfigParser()
        self.config_file = os.path.join(os.getenv("HOME"),
                                        ".config/rdesk/rdesk.config")
        print "FILE: %s"%self.config_file
        if not os.access(self.config_file, os.F_OK):
            dir_name = os.path.dirname(self.config_file)
            print "DIR: %s"%dir_name
            if os.access(dir_name, os.F_OK):
                if not os.path.isdir(dir_name):
                    print("Failed to check config file: %s exists, \
but it's not a directory")
                    sys.exit(1)
            else:
                cmd = "mkdir -p "+dir_name
                print "Creating", cmd
                p = Popen(cmd, shell=True)
                sts = os.waitpid(p.pid, 0)
                if sts[1] != 0:
                    print "Failed to create directory: %s"%dir_name
                    print "Please create it manually and chmod for me."
                    sys.exit(1)

        self.configs = {}
        self.configs["APP"] = "rdesktop"
        self.configs["GEO"] = "800x600"
        self.configs["PCs"] = []

    def read_config(self):
        try:
            fn = self.parser.read(self.config_file)
        except ConfigParser.ParsingError:
            print ("Failed to parse file")
            print sys.exc_info()
            return -1

        if not fn:
            print "Noting read from file, using default."
        else:
            try:
                self.configs["APP"] = self.parser.get("GLOBAL", "app")
                self.configs["GEO"] = self.parser.get("GLOBAL", "geo")
                # self.configs["DEP"] = self.parser.get("GLOBAL", "DEP")#depth
            except:
                print("Exception occurred, will using default value.")
                print sys.exc_info()

            item = {}
            for sec in self.parser.sections():
                if sec == "GLOBAL":
                    continue
                try:
                    item["ip"] = sec
                    item["username"] = self.parser.get(sec, "username")
                    item["password"] = self.parser.get(sec, "password")
                except:
                    print("failed to get desired contents")
                    print sys.exc_info()
                    continue
                else:
                    self.configs["PCs"].append(deepcopy(item))
        return 0

    def dump(self):
        print "dump called."
        fd = open(self.config_file, "w")
        for sec in self.parser.sections():
            self.parser.remove_section(sec)

        if not self.parser.has_section("GLOBAL"):
            self.parser.add_section("GLOBAL")
        self.parser.set("GLOBAL", "APP", self.configs["APP"])
        self.parser.set("GLOBAL", "GEO", self.configs["GEO"])
        print "AA:", self.configs["APP"], self.configs["GEO"]

        for obj in self.configs["PCs"]:
            self.parser.add_section(obj["ip"])
            self.parser.set(obj["ip"], "username", obj["usr"])
            self.parser.set(obj["ip"], "pw", obj["passwd"])

        self.parser.write(fd)
        fd.flush()
        fd.close()
        print "finished."

if __name__ == '__main__':
    print ("OK")
    global config
    config = RD_Config()

    ret = config.read_config()
    if ret == -1:
        print "Failed to read configuration file."
        sys.exit(1)
    # else:
    #     print "Writing ..."
    #     config.dump()

    app = wx.App()

    frame = Frame(config)

    app.MainLoop()
