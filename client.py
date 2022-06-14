"""
Run the following command to start the client

python3 client.py <start_port> <end_port> <md5_password> <max_password_length> <clear_password> <isPrintable>

For example, python3 client.py 5000 5002 ea416ed0759d46a8de58f63a59077499 4 xxxx 0

Note:
- When starting the client, we have the option of omitting both `<clear_password>` and `<isPrintable>` 
or having both of them on the terminal. We can't keep only one or another. `<clear_password>` is just the 
clear text password of the `<md5_password>` which is used to determine the average crack time in part4. 
`<isPrintable>` is a flag where "1" means the search space is made by printable characters (length 100) and 
"0" means the search space is made by ascii lowercase characters (length 26). If omitting both 
`<clear_password>` and `<isPrintable>`, the default search space is formed by printable characters.
- After we start the service, we should know the range of the port for <start_port> and <end_port>.
"""

#import libraries
from flask import Flask
import requests
import json
import sys
from threading import Thread 
import time
import socket
import numpy as np
import random
import time

#start the timer to find average crack time for part4
start_time = time.process_time()

#retrieve arguments from the command
if len(sys.argv) == 7:
    clear_password = sys.argv[5] #for part 4 to check if we have fonud the password or not
    isPrintable = sys.argv[6] #for part 4: 1 is true, 0 is false (for ascii lowercase)
else:
    clear_password = ""
    isPrintable = "1"

start_port = sys.argv[1]
end_port = sys.argv[2]
md5_password = sys.argv[3]
max_password_length = sys.argv[4]
headers = {"Content-Type": "application/json"}

#for part 3, socket are used to determine is a port down or not
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#start a class object thread to crack passwords
class Crack_Password_In_Partitioned_Search_Space:
    def crack_password(self):
        url = "http://127.0.0.1:"+str(self._port)

        #for part 3, use try except block for fault tolerance
        try:
            #POST 
            r = requests.post(url+"/hashedPasswords" ,data=json.dumps({"hashed_password": md5_password, 
            "max_length": self._max_password_length, "first_char_start_index": str(self._start_index), 
            "first_char_end_index": str(self._end_index), "isPrintable": isPrintable}), headers = headers)
            
            #GET
            response = requests.get(url + "/hashedPasswords/"+md5_password)

            #show output on the client terminal
            print("From crack_password port", self._port, "with start index", str(self._start_index),
            "and end index", str(self._end_index),", and the cracked password is:",
            response.json()["cleartext_password"])

            #for part 4, stop the timer when the system crack the password
            if response.json()["cleartext_password"] == clear_password:
                print("Password cracking time is:", time.process_time() - start_time, "seconds")
                
        except Exception as exception:
            #for part 3, when a user terminates a service during password cracking
            print("A connection error by CRTL + C, port",str(self._port),"down")

            # append current task to start_index_task_array and end_index_task_array
            # increase task_num by 1 to ensure we re-run the serach space
            global start_index_task_array
            start_index_task_array.append(self._start_index)
            global end_index_task_array
            end_index_task_array.append(self._end_index)
            global task_num
            task_num+=1
        
    #start the thread here
    def __init__(self, max_password_length, port, start_index, end_index, isPrintable):
        self._max_password_length = max_password_length
        self._port = port
        self._start_index = start_index
        self._end_index = end_index
        self._isPrintable= isPrintable
        self._t = Thread(target=self.crack_password)
        self._t.start()
        
#PARTITION RULE: splitting the search space by the first character and divide it to 2*service_num parts
service_num = int(end_port)-int(start_port)+1

if isPrintable == "1":
    length_of_ascii_chars = 100 
else:
    length_of_ascii_chars = 26

length_per_chunk = int(length_of_ascii_chars/(2*service_num))

start_index_task_array = list(np.arange(0,length_of_ascii_chars,length_per_chunk))
end_index_task_array = []
for index in start_index_task_array:
    if index+length_per_chunk-1 > length_of_ascii_chars:
        end_index_task_array.append(length_of_ascii_chars-1)
    else:
        end_index_task_array.append(index+length_per_chunk-1)

#shuffle the chunks, so that we don't always start from aaaa and causing zzzz to be checked last
indices = list(np.arange(0,len(start_index_task_array),1))
random.shuffle(indices)

start_tmp = []
end_tmp = []
for i in indices:
    start_tmp.append(start_index_task_array[i])
    end_tmp.append(end_index_task_array[i])
    
start_index_task_array = start_tmp
end_index_task_array = end_tmp


task_num = len(start_index_task_array) # can also be len(end)

#automatically create thread variable
#refer to this website: https://python.plainenglish.io/how-to-dynamically-declare-variables-inside-a-loop-in-python-21e6880aaf8a
task_complete_count = 0

for i in range(service_num):
    #for part 3, use try except block for fault tolerance
    try:
        #GET
        requests.get("http://127.0.0.1:"+str(int(start_port)+i))
        globals()[f'thread_{i+1}'] = Crack_Password_In_Partitioned_Search_Space(max_password_length, 
        int(start_port)+i, start_index_task_array[task_complete_count], 
        end_index_task_array[task_complete_count], isPrintable)
        task_complete_count+=1

    except Exception as exception:
        print("Setup Error: a connection error is identified, port",int(start_port)+i,"down")
    
while task_complete_count < task_num:
    # continue to distribute chunks of search space to a available service
    for i in range(service_num):
        # for part 3, use try except block for fault tolerance to check if a service is down or not
        try:
            #GET
            requests.get("http://127.0.0.1:"+str(int(start_port)+i))
            if globals()[f'thread_{i+1}']._t.is_alive() == False:
                globals()[f'thread_{i+1}'] = Crack_Password_In_Partitioned_Search_Space(max_password_length, 
                int(start_port)+i, start_index_task_array[task_complete_count], 
                end_index_task_array[task_complete_count], isPrintable)
                
                task_complete_count+=1
                
        except Exception as exception:
            pass