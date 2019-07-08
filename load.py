
# -*- coding: utf-8 -*- 
import sys
from Modules.debug import debug

this = sys.modules[__name__]
this.version="0.0.0"



def plugin_start(plugin_dir):
   """
   Load this plugin into EDMC
   """
   debug("Плагин запущен")
   return "EGP-Plugin".format(this.version)