#ftp upload
from ftplib import FTP
import os

def upload(server_name, user, password):
    ftp = FTP(server_name)
    print('connected')
    ftp.login(user, password)
    print('login')
    try:
        server_files = ftp.nlst("*.cca")
    except:
        server_files= []
    print('server check')
    local_files = os.listdir()
    new_local=[lfile for lfile in local_files if '.cca' in lfile and lfile not in server_files]
    for filename in new_local:
        print('uploading:', filename)
        fp = open(filename, 'rb')
        ftp.storbinary('STOR '+filename,fp)
        fp.close()
    ftp.close()

def download(server_name, user, password):
    ftp = FTP(server_name)
    ftp.login(user, password)
    server_files = ftp.nlst("*.cca")
    local_files = os.listdir()
    new_local=[sfile for sfile in server_files if sfile not in local_files]
    if new_local == []:
        print('No new files')
        return 0
    for filename in new_local:
        print('downloading:', filename)
        fp = open(filename, 'ab')
        ftp.retrbinary('RETR '+filename, fp.write)
        fp.close()
    ftp.close()

#server_name = 'host3.bakop.com'
#user = 'instrumentacioncca'
#password = 'instrumentacion'
#upload(server_name, user, password)
