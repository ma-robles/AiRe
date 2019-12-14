import time
from ftplib import FTP

#server_name = 'host3.bakop.com'
#user = 'instrumentacioncca'
#password = 'instrumentacion'

server_name = '132.248.8.29'
user ='web_ruoa'
password = 'ru04cc4'
while(True):
    try:
        ftp = FTP(server_name)
        print('connected')
        ftp.login(user, password)
        print('login')
        ftp.cwd('/var/www/pembu_miguel')
        print('uploading minute data...')
        with open('minute.cca', 'rb') as fp:
            ftp.storbinary('STOR minute.cca',fp)
        ftp.close()
        
    except:
        print('error uploading')
    time.sleep(30)
