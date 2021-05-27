import serial
from datetime import datetime as DT
import datalog as dlog
import time
from sys import argv
import post
import numpy as np
from gpiozero import LED

def raw2int(data):
    new_data = []
    #UV
    new_data.append(int.from_bytes(data[0:2],'big'))
    #SUN
    new_data.append(int.from_bytes(data[2:4],'big'))
    #Wdir
    new_data.append(data[4])
    #Wspeed
    new_data.append(data[5])
    #Rain
    new_data.append(data[6])
    #temperature
    new_data.append(int.from_bytes(data[7:9],'big'))
    #Humidity
    new_data.append(data[9])
    #Pressure
    new_data.append(int.from_bytes(data[10:13],'big'))
    #batt
    new_data.append(int.from_bytes(data[13:15],'big'))
    
    return new_data

def int2val(data):
    new_data = []
    new_data.append(dlog.to_uv(data[0]))
    new_data.append(dlog.to_sun(data[1]))
    wc = dlog.to_comp(data[2],dlog.to_wspeed(data[3]))
    new_data.append(wc[0])
    new_data.append(wc[1])
    new_data.append(dlog.to_rain(data[4]))
    new_data.append(dlog.to_temp(data[5]))
    new_data.append(dlog.to_HR(data[6],new_data[-1]))
    new_data.append(dlog.to_mbar(data[7]))
    new_data.append(dlog.to_batt(data[8]))
    return new_data


#turn ON ARLEN
pwr= LED(16)
pwr.on()
print("ARLEN ON")
#port_name = '/dev/ttyUSB0'
#port_name = '/dev/ttyAMA0'
try:
    port_name=argv[2]
except:
    port_name = '/dev/ttyS0'
print('Puerto:', port_name)
#init data
my_minute = DT.strftime(DT.now(), '%Y-%m-%d %H:%M')
v_file = 'values.cca'
names={
        'uv':0,
        'sun':1,
        'ws':2,
        'wd':3,
        'rain':4,
        'temp':5,
        'hr':6,
        'pres':7,
        'vbat':8,
        }
header_s = 'Fecha,UV,Radiación,WS,WD,Lluvia,Temperatura,Humedad,Presión,vBat,Tmin,Tmax,WSmax'
#id name, must include '_'
pre_name=argv[1]
#minimum data required
min_data=10
data_array=[]
data_varray=[]
while(True):
  try:
    with serial.Serial(port_name) as ser:
        #get data
        start_data = b'0'
        #add timeout to this loop
        while int.from_bytes(start_data,'big')!=0xaa:
            start_data = ser.read()
        data_pack = ser.read(15)
        checksum = int.from_bytes(ser.read(),'big')
        c_checksum = sum(data_pack,0xaa)&0xff
        if checksum!=c_checksum:
            continue
        #convert
        #print(data_pack)
        data_pack = raw2int(data_pack)
        data_pack = int2val(data_pack)
        #add data
        data_array.append(data_pack)
        #polar wind version
        idata = data_pack[:]
        #wind convertion
        wind_c = dlog.c_to_v(data_pack[2], data_pack[3])
        #saving
        #r
        idata[names['ws']] = wind_c[0]
        #angle
        idata[names['wd']] = wind_c[1]
        data_varray.append(idata)
        #data to string
        str_data = ["{:.2f}".format(number) for number in idata]
        str_data = ','.join(str_data)
        #check time
        my_now = DT.now()
        mytime = DT.strftime(my_now, '%Y-%m-%d %H:%M:%S')
        new_minute = DT.strftime(my_now, '%Y-%m-%d %H:%M')
        #save current data
        with open(v_file, 'w') as values_file:
            print(mytime, str_data, file= values_file, sep=',')
        #print to stdout
        print(mytime, str_data)
        #end of minute
        if new_minute != my_minute:
            #update minute
            my_minute = new_minute
            #convert array to numpy
            data_array=np.array(data_array)
            data_varray=np.array(data_varray)
            #check min size
            n_samples=data_array.shape[0]
            if n_samples<min_data:
                data_array=[]
                data_varray=[]
                continue
            #detect outliers
            press_col=data_array.T[names['pres']]
            outliers=post.detect_outlier_mad(press_col)
            #deleting outliers
            data_array=data_array[np.logical_not(outliers)]
            data_varray=data_varray[np.logical_not(outliers)]
            print('minute:', new_minute, n_samples,data_array.shape[0])
            #max wind speed
            ws_imax=np.argmax(data_varray.T[names['ws']])
            ws_max=data_varray.T[names['ws']][ws_imax]
            wd_max=data_varray.T[names['wd']][ws_imax]
            min_temp=np.min(data_array.T[names['temp']])
            max_temp=np.max(data_array.T[names['temp']])
            #acc values
            data_acc=np.sum(data_array, axis=0)
            #get accumulated rain
            rain_acc= data_acc[names['rain']]
            #output vector
            #mean
            data_out=np.mean(data_array, axis=0)
            #add rain
            data_out[names['rain']]=rain_acc
            #wind convertion
            ws,wd=dlog.c_to_v(data_out[names['ws']],data_out[names['wd']])
            data_out[names['ws']]=ws
            data_out[names['wd']]=wd
            data_out=np.around(data_out,decimals=2)
            #save
            h_file = pre_name+DT.strftime(my_now, '%Y-%m-%d')+'_raw.cca'
            #by-day file
            with open(h_file, 'a') as values_file:
                str_data = ["{}".format(number) for number in data_out]
                str_data = ','.join(str_data)
                print(mytime, 
                        str_data,
                        min_temp,
                        max_temp,
                        ws_max,
                        wd_max,
                        file= values_file,
                        sep=',',
                        )
            #by-minute file
            with open('minute.cca', 'w') as minute_file:
                print(header_s,
                        file=minute_file,
                        )
                print(mytime, 
                        str_data,
                        min_temp,
                        max_temp,
                        ws_max,
                        wd_max,
                        file= minute_file,
                        sep=',',
                        )
            data_array=[]
            data_varray=[]
  except Exception as e:
    print("error!!!", e)
    data_array=[]
    data_varray=[]
    time.sleep(10)
