'''
file processing tools
'''

from sys import argv
from subprocess import Popen
import os
import numpy as np

def get_files(path, file_filter):
    '''
    get files in path with file_filter
    return a list
    '''
    list_file=[]
    root_dir=os.path.join(os.getcwd(), path)
    root_dir=os.path.normpath(root_dir)
    wgen=os.walk(root_dir)
    dir_hidden=''
    for root,dirs,files in wgen:
        dir_name=os.path.basename(root)
        if len(dir_name)>0:
            if dir_name[0]=='.':
                dir_hidden=dir_name
                continue
        if dir_hidden!='':
            if dir_hidden in root:
                continue
        for f in files:
            if file_filter in f:
                list_file.append(os.path.join(root,f))
    list_file.sort()
    return list_file

def from_file(ivars, ovars, filename, ofilename, sep=','):
    '''
    reorder data from original idic to odic
    ivars: list of input parameter sequence
    ovars: list output parameter sequence, can be shorter than ivars
    filename: original file
    ofilename: output filename
    '''
    ilen=len(ivars)
    with open(ofilename, 'w') as ofile:
        print('',file=ofile)
    with open(filename,'r') as ifile:
        for line in ifile:
            dic_vars={}
            #remove end garbage chars
            data=line.rstrip()
            #test for correct data split
            try:
                data=data.split(sep)
            except:
                continue
            if len(data)<ilen:
                continue
            #create data dictionary
            for i,key in enumerate(ivars):
                dic_vars[key]=data[i]
            #output data
            new_line=[]
            with open(ofilename, 'a') as ofile:
                for key in ovars:
                    new_line.append(dic_vars[key])
                print(','.join(new_line),file=ofile)

def detect_outlier_std(data, nstd=3):
    '''
    detect outliers using standard deviation
    data - vector data 
    nstd - standard deviations from the mean
    return - detected outlier index numpy array
    '''
    dmean = np.mean(data)
    rm = np.std(data)
    low = dmean-rm
    high = dmean+rm
    return np.any([data<low, data>high], axis=0)

def detect_outlier_mad(data, nmad=3):
    '''
    detect outlier using median absolute deviation
    data - vector data
    nmad - mad from the median
    return - detected outlier index from numpy array
    '''
    #b=1/Q(75)
    b=1.4826
    med=np.median(data)
    mad= np.abs(data-med)
    mad= b*np.median(mad)
    if mad==0:
        mad=med/100
    low= med-nmad*mad
    high= med+nmad*mad
    print('med:',med, 'mad:',mad)
    return np.any([data<low, data>high], axis=0)

def rm_outlier_iqr(data, niqr=1.5):
    '''
    delete outliers data using interquartile range method
    data - data
    niqr - times iqr from 25 and 75 percentile
    '''
    pass
