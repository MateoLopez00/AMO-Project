#!/usr/bin/env python
# coding: utf-8

# In[4]:


#Defining the database of instruments
#see: https://www.datasciencecourse.org/notes/relational_data/
import pandas as pd


# In[24]:


def orchestra_database():
    # Instrument IDs from:
    #https://www.ccarh.org/courses/253/handout/gminstruments/
    #Instrument ranges from:
    #https://soundprogramming.net/file-formats/midi-note-ranges-of-orchestral-instruments/
    instruments = pd.DataFrame([(40, 'violin', 55,103), 
                       (41, 'viola', 48,91),
                       (42, 'cello', 36,76), 
                       (43, 'bass', 28,67),
                       (73, 'flute', 60,96),
                       (68, 'oboe', 58,91), 
                       (71, 'clarinet', 50,94), 
                       (70, 'bassoon', 34,75), 
                       (60, 'horn', 34,77), 
                       (56, 'trumpet', 55,82)],  
                      columns=["idi", "name", "min_rage","max_rage"])
    instruments['idi'] = instruments['idi'].astype(int)
    instruments['min_rage'] = instruments['min_rage'].astype(int)
    instruments['max_rage'] = instruments['max_rage'].astype(int)
    instruments['name'] = instruments['name'].astype(str)
    
    combos = pd.DataFrame([(1, 'Tuti'), 
                           (2, 'Strings'),
                           (3, 'Woods'),
                           (4, 'Brasses'),
                           (5, 'Strings-Woods'),
                           (6, 'Strings-Brasses')],  
                      columns=["idc", "name"])
    combos['idc'] = combos['idc'].astype(int)
    combos['name'] = combos['name'].astype(str)
    
    combo_inst = pd.DataFrame([
                       (1, 41),
                       (1, 42),
                       (1, 43),
                       (1, 73),
                       (1, 68),
                       (1, 71),
                       (1, 70),
                       (1, 60),
                       (1, 56),
                       (2, 40), 
                       (2, 41),
                       (2, 42),
                       (2, 43),
                       (3, 73),
                       (3, 68),
                       (3, 71),
                       (3, 70),
                       (4, 60),
                       (4, 56)
                       ],  
                  columns=["idc", "idi"])
    combo_inst['idc'] = combo_inst['idc'].astype(int)
    combo_inst['idi'] = combo_inst['idi'].astype(int)
    return instruments, combos, combo_inst

