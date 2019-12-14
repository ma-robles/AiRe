#ftp upload
from ftplib import FTP
import os

def get_update_list(server_name, user, password, name_filter):
    print('server connection...', end= ' ')
    ftp = FTP(server_name)
    print('OK')
    print('login...',end=' ')
    ftp.login(user, password)
    print('OK')
    print('Get server file list...')
    try:
        server_all = ftp.mlsd("./", facts=['size'])
    except:
        server_all = []
    server_list={}
    for sfile in server_all:
        if name_filter in sfile[0]:
            server_list[sfile[0]]=int(sfile[1]['size'])

    ftp.close()
    print('OK')
    for l in server_list.keys():
        print(l,server_list[l])
    print('Get local list...', end=' ')
    local_all= os.listdir()
    local_list={}
#new_local=[lfile for lfile in local_files if '.cca' in lfile and lfile not in server_files]
    for filename in local_all:
        if name_filter in filename:
            local_list[filename] = os.lstat(filename).st_size
    print('OK')

    for l in local_list.keys():
        print(l,local_list[l])
    print('compare')
    update_list = []
    for i in local_list.keys():
        if i in server_list.keys():
            if server_list[i]<local_list[i]:
                update_list.append(i)
        else:
            update_list.append(i)

    return update_list

#connection
server_name = "132.248.8.31"
user = 'pembu'
password = 'p3mbu'
name_filter = '.py'
update_list = get_update_list(server_name, user, password, name_filter)

print('update list')
ftp = FTP(server_name)
ftp.login(user, password)
for filename in update_list:
    print('uploading:', filename)
    with open(filename, 'rb') as fp:
        ftp.storbinary('STOR '+filename,fp)
ftp.close()
