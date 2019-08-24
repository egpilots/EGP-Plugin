
# -*- coding: utf-8 -*- 
import sys
from Modules.debug import debug
from Modules.debug import Debug

from config import config
import myNotebook as nb
from urllib import quote_plus
import requests
import json
import webbrowser
import Tkinter as tk
from ttkHyperlinkLabel import HyperlinkLabel
import myNotebook as nb

#Переменные, необходимые для функционирования плагина
this = sys.modules[__name__]
myPlugin = 'EGP-Plugin'

this.version="0.0.0"
this.client_version='{}.{}'.format(myPlugin,this.version)


def plugin_start(plugin_dir):
   """
   Load this plugin into EDMC
   """
   Debug.setClient(this.client_version)
   
   

   debug("Плагин запущен")


   return "EGP-Plugin".format(this.version)



def plugin_prefs(parent, cmdr, is_beta):
    '''
    Return a TK Frame for adding to the EDMC settings dialog.
    '''
    
    frame = nb.Frame(parent)
    frame.columnconfigure(1, weight=1)
    
    
    #this.release.plugin_prefs(frame, cmdr, is_beta,2)
    
    Debug.plugin_prefs(frame,this.client_version,1)
   

    PADX = 10
    BUTTONX = 12	# indent Checkbuttons and Radiobuttons
    PADY = 2		# close spacing

    
    

    HyperlinkLabel(frame, text='Inara', background=nb.Label().cget('background'), url='https://inara.cz/', underline=True).grid(columnspan=2, padx=PADX, sticky=tk.W)	# Don't translate
    this.log = tk.IntVar(value = config.getint('EGP_out') and 1)
    this.log_button = nb.Checkbutton(frame, text=_('Send flight log and Cmdr status to Inara'), variable=this.log, command=prefsvarchanged)
    this.log_button.grid(columnspan=2, padx=BUTTONX, pady=(5,0), sticky=tk.W)

    nb.Label(frame).grid(sticky=tk.W)	# big spacer
    this.label = HyperlinkLabel(frame, text=_('EGP credentials'), background=nb.Label().cget('background'), url='https://inara.cz/settings-api', underline=True)	# Section heading in settings
    this.label.grid(columnspan=2, padx=PADX, sticky=tk.W)

    this.apikey_label = nb.Label(frame, text=_('API Key'))	# EDSM setting
    this.apikey_label.grid(row=12, padx=PADX, sticky=tk.W)
    this.apikey = nb.Entry(frame)
    this.apikey.grid(row=12, column=1, padx=PADX, pady=PADY, sticky=tk.EW)

    prefs_cmdr_changed(cmdr, is_beta)

    return frame

def prefs_cmdr_changed(cmdr, is_beta):
    this.log_button['state'] = cmdr and not is_beta and tk.NORMAL or tk.DISABLED
    this.apikey['state'] = tk.NORMAL
    this.apikey.delete(0, tk.END)
    if cmdr:
        cred = credentials(cmdr)
        if cred:
            this.apikey.insert(0, cred)
    this.label['state'] = this.apikey_label['state'] = this.apikey['state'] = cmdr and not is_beta and this.log.get() and tk.NORMAL or tk.DISABLED

def prefsvarchanged():
    this.label['state'] = this.apikey_label['state'] = this.apikey['state'] = this.log.get() and this.log_button['state'] or tk.DISABLED

def prefs_changed(cmdr, is_beta):
    changed = config.getint('EGP_out') != this.log.get()
    config.set('EGP_out', this.log.get())



    if cmdr and not is_beta:
        this.cmdr = cmdr
        this.FID = None
        cmdrs = config.get('EGP_cmdrs') or []
        apikeys = config.get('EGP_apikeys') or []
        if cmdr in cmdrs:
            idx = cmdrs.index(cmdr)
            apikeys.extend([''] * (1 + idx - len(apikeys)))
            changed |= (apikeys[idx] != this.apikey.get().strip())
            apikeys[idx] = this.apikey.get().strip()
        else:
            config.set('EGP_cmdrs', cmdrs + [cmdr])
            changed = True
            apikeys.append(this.apikey.get().strip())
        config.set('EGP_apikeys', apikeys)

        if this.log.get() and changed:
            this.newuser = True	# Send basic info at next Journal event
            add_event('getCommanderProfile', time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), { 'searchName': cmdr })
            call()




def credentials(cmdr):
    # Credentials for cmdr
    if not cmdr:
        return None

    cmdrs = config.get('inara_cmdrs') or []
    if cmdr in cmdrs and config.get('inara_apikeys'):
        return config.get('inara_apikeys')[cmdrs.index(cmdr)]
    else:
        return None


def plugin_stop():
    """
    EDMC is closing
    """
    print "Farewell cruel world!"