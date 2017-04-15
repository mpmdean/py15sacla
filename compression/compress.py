#!/home/mdean/anaconda3/bin/python

import sys
import fileinput 
from shutil import copy
import subprocess 

if len(sys.argv) == 2:
    run = sys.argv[1]
    copy('/home/mdean/datacompressing/comp1file.py', 
         '/home/mdean/datacompressing/temp_comp.py')
    #print("running {}".format(run))
    for line in fileinput.input('temp_comp.py', inplace=True):
        print(line.replace('run = ', 'run = {}'.format(run)), end='')
    
    subprocess.run(['chmod', '+x', '/home/mdean/datacompressing/temp_comp.py'])
    subprocess.run(["qsub", "/home/mdean/datacompressing/temp_comp.py"])

elif len(sys.argv) == 3:
    for run in range(int(sys.argv[1]), int(sys.argv[2])+1):
        copy('/home/mdean/datacompressing/comp1file.py', 
               '/home/mdean/datacompressing/temp_comp.py')
        #print("running {}".format(run))
        for line in fileinput.input('/home/mdean/datacompressing/temp_comp.py', inplace=True):
            print(line.replace('run = ', 'run = {}'.format(run)), end='')
        
        subprocess.run(['chmod', '+x', '/home/mdean/datacompressing/temp_comp.py'])
        subprocess.run(["qsub", "/home/mdean/datacompressing/temp_comp.py"])  
            
