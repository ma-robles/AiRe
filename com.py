import serial
from datetime import datetime as DT
import datalog as dlog
import time

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

def int2str(data):
    strdata = '{d[0]:.1f},'.format(d=data)
    strdata += '{d[1]:.0f},'.format(d=data)
    strdata += '{d[2]:.1f},'.format(d=data)
    strdata += '{d[3]:.0f},'.format(d=data)
    strdata += '{d[4]:.1f},'.format(d=data)
    strdata += '{d[5]:.1f},'.format(d=data)
    strdata += '{d[6]:.0f},'.format(d=data)
    strdata += '{d[7]:.1f},'.format(d=data)
    strdata += '{d[8]:.1f},'.format(d=data)
    strdata += '{d[9]:.1f},'.format(d=data)
    strdata += '{d[10]:.1f},'.format(d=data)
    strdata += '{d[11]:.1f}'.format(d=data)
    return strdata
def int2str2(data):
    strdata = '{d[0]:.1f},'.format(d=data)
    strdata += '{d[1]:.0f},'.format(d=data)
    strdata += '{d[2]:.1f},'.format(d=data)
    strdata += '{d[3]:.0f},'.format(d=data)
    strdata += '{d[4]:.1f},'.format(d=data)
    strdata += '{d[5]:.1f},'.format(d=data)
    strdata += '{d[6]:.0f},'.format(d=data)
    strdata += '{d[7]:.1f},'.format(d=data)
    strdata += '{d[8]:.1f}'.format(d=data)
    return strdata


#port_name = '/dev/ttyUSB0'
#port_name = '/dev/ttyAMA0'
port_name = '/dev/ttyS0'
print('Puerto abierto')
#init data
my_minute = DT.strftime(DT.now(), '%Y-%m-%d %H:%M')
n_samples = 0
acc_data = [0,0,0,0,0,0,0,0,0]
v_file = 'values.cca'
max_temp = float('-inf')
min_temp = float('inf')
max_vel = float('-inf')
header_s = 'Fecha,UV,Radiación,WS,WD,Lluvia,Temperatura,Humedad,Presión,vBat,Tmin,Tmax,WSmax'
while(True):
  try:
    with serial.Serial(port_name) as ser:
    #while(True):
        #get data
        start_data = b'0'
        while int.from_bytes(start_data,'big')!=0xaa:
            start_data = ser.read()
        data_pack = ser.read(15)
        checksum = int.from_bytes(ser.read(),'big')
        c_checksum = sum(data_pack,0xaa)&0xff
        if checksum!=c_checksum:
            continue
        #convert
        print(data_pack)
        data_pack = raw2int(data_pack)
        data_pack = int2val(data_pack)
        idata = data_pack[:]
        wind_c = dlog.c_to_v(data_pack[2], data_pack[3])
        #r
        idata[2] = wind_c[0]
        #angle
        idata[3] = wind_c[1]
        if wind_c[0]>max_vel:
            max_vel = wind_c[0]
        if data_pack[5]>max_temp:
            max_temp = data_pack[5]
        if data_pack[5]<min_temp:
            min_temp = data_pack[5]
        
        n_samples+=1
        for i,d in enumerate(data_pack):
            #print(i,d)
            acc_data[i] += d
        str_data = int2str2(idata)
        my_now = DT.now()
        mytime = DT.strftime(my_now, '%Y-%m-%d %H:%M:%S')
        new_minute = DT.strftime(my_now, '%Y-%m-%d %H:%M')
        #actual
        with open(v_file, 'w') as values_file:
            print(mytime, str_data, file= values_file, sep=',')
        print(mytime, str_data)
        if new_minute != my_minute:
            print('minute:', new_minute)
            my_minute = new_minute
            for i,d in enumerate(acc_data):
                if i!=4:
                    acc_data[i]/=n_samples
            n_samples = 0
            acc_data[2],acc_data[3] = dlog.c_to_v(acc_data[2],acc_data[3])
            h_file = DT.strftime(my_now, '%Y-%m-%d')+'_raw.cca'
            with open(h_file, 'a') as values_file:
                print(mytime, 
                        int2str(acc_data+[min_temp,max_temp,max_vel]),
                        file= values_file,
                        sep=',',
                        )
            with open('minute.cca', 'w') as minute_file:
                print(header_s,
                        file=minute_file,
                        )
                print(mytime, 
                        int2str(acc_data+[min_temp,max_temp,max_vel]),
                        file= minute_file,
                        sep=',',
                        )
            max_temp = float('-inf')
            min_temp = float('inf')
            max_vel = float('-inf')
            acc_data = [0,0,0,0,0,0,0,0,0]
  except:
    print("error!!!")
    time.sleep(10)
