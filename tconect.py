import connect_lib as conn
import time

#server_name = 'host3.bakop.com'
#user = 'instrumentacioncca'
#password = 'instrumentacion'

server_name = '132.248.8.31'
user ='pembu'
password = 'p3mbu'

while(True):
    try:
        conn.upload(server_name, user, password)
        print('success upload')
    except:
        print('error uploading')
    time.sleep(600)
        
