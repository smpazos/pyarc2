# -*- coding: utf-8 -*-
"""
Created on Wed Jun 12 10:46:06 2024

@author: pazossm
"""

from pyarc2 import Instrument, find_ids

def connect2arc():
    
    # Get the ID of the first available ArC TWO
    arc2id = find_ids()[0]
    
    # firmware; shipped with your board
    fw = 'efm03_20220905.bin'
    
    # connect to the board
    arc = Instrument(arc2id, fw)
    
    return arc