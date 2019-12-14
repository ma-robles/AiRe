from math import cos
from math import sin
from math import pi
from math import atan2
from math import degrees
from math import sqrt

def to_uv(data):
#UV index
    return data/47

def to_sun(data):
#W/m2
    return 1.9297*data

def to_comp(w_dir, w_speed):
#W dir 0-1023
    w_dir *= pi/128
    #NS
    NS = w_speed*cos(w_dir)
    #EW
    EW = w_speed*sin(w_dir)
    return NS,EW

def c_to_v(ns, ew):
    angle = atan2(ew, ns)
    angle = degrees(angle)
    if angle<=0:
        angle+=360
    r = pow(ns,2)+pow(ew,2)
    r = sqrt(r)
    if r == 0:
        angle=0
    return r, angle

def to_wspeed(data):
#to m/s
    return data*0.44

def to_rain(data):
#to mm
    return data*0.2

def to_temp(temp):
    '''
    convierte de datos crudos a temperatura
    '''
    t=temp*0.04-39.6
    return t

def to_HR(humedad,temp):
    '''
    convierte de datos crudos a HR,
    compensa con temperatura
    '''
    HR=-4+0.648*humedad-.00072*(humedad**2)
    #compensando humedad con temperatura
    HR+=(temp-25)*(0.01+0.00128*humedad)
    return HR

def to_mbar(pres):
    return pres/100

def to_batt(v):
    r1=22000
    r2=47000
    k = r1/(r2+r1)
    return v*(3.3/1024)/k
