"""
Open multiple terminals and on each terminal run: 

python3 cracker_service.py <port>

For example, python3 cracker_service.py 5000 (on one terminal)
             python3 cracker_service.py 5001 (on second terminal)
             python3 cracker_service.py 5002 (on third terminal)
Note: the port number on each terminal should be different, and have a difference of +1
# following a trend such as 5000, 5001, 5002, ... 5011, etc.
"""
import sys
import itertools
import string
import hashlib
from flask import Flask, request

app = Flask(__name__)

# define cache and use md5_password as index and value are max_length, 
# first_char_start_index, first_char_end_index, and other related attributes
password_cracked_cache = {}
password_cracked={}

# GET ACTION
@app.route('/hashedPasswords/<path:path>', methods = ["GET"])
def get_crack_password(path):
    crack_result = password_cracked[path]
    return crack_result, 200

# POST ACTION
@app.route('/hashedPasswords', methods = ["POST"])
def create_crack_password():
    md5_password = request.json['hashed_password']
    max_length = int(request.json['max_length'])
    first_char_start_index = int(request.json['first_char_start_index'])
    first_char_end_index = int(request.json['first_char_end_index'])
    isPrintable = request.json['isPrintable']
    
    # check cache before cracking the password
    if md5_password in password_cracked_cache:
        for entry in password_cracked_cache[md5_password]:
            if entry['max_length'] == max_length and entry['first_char_start_index'] == first_char_start_index and entry['first_char_end_index'] == first_char_end_index:
                #if found in cache, then just use cache output
                print("Use cached result!")
                password_cracked[md5_password] = {'hashed_password': md5_password,'cleartext_password': entry['cleartext_password']}
                return password_cracked[md5_password], 201

        #run crack password
        crack_result = bruteforce_password_given_first_char(md5_password, max_length, first_char_start_index, first_char_end_index,isPrintable)
        entry = {'hashed_password': md5_password,'cleartext_password': crack_result, 'max_length':max_length, 'first_char_start_index': first_char_start_index, 'first_char_end_index':first_char_end_index}
        password_cracked_cache.setdefault(md5_password, [])
        password_cracked_cache[md5_password].append(entry)
        password_cracked[md5_password] = {'hashed_password': md5_password,'cleartext_password': crack_result}
        return password_cracked[md5_password], 201
    else:
        #run crack password
        crack_result = bruteforce_password_given_first_char(md5_password, max_length, first_char_start_index, first_char_end_index,isPrintable)
        entry = {'hashed_password': md5_password,'cleartext_password': crack_result, 'max_length':max_length, 'first_char_start_index': first_char_start_index, 'first_char_end_index':first_char_end_index}
        password_cracked_cache.setdefault(md5_password, [])
        password_cracked_cache[md5_password].append(entry)
        password_cracked[md5_password] = {'hashed_password': md5_password,'cleartext_password': crack_result}
        return password_cracked[md5_password], 201

#this helper function cracks the password
def bruteforce_password_given_first_char(hashed_password, max_length, first_char_start_index, first_char_end_index,isPrintable):
    
    if isPrintable == "1":
        chars = string.printable[first_char_start_index:first_char_end_index+1] # all printable characters 
        search_space = string.printable
    else:
        chars = string.ascii_lowercase[first_char_start_index:first_char_end_index+1] # lowercase characters 
        search_space = string.ascii_lowercase
    
    for char in chars:
        for password_length in range(1, max_length): # here we get rid of the +1
            for guess in itertools.product(search_space, repeat=password_length):
                guess = "".join(guess)
                guess = char+guess
                
                if hashlib.md5(guess.encode()).hexdigest() == hashed_password:
                    return guess
    
    return None

# start a main function for the cracker_service
if __name__ == '__main__': 
    if len(sys.argv) !=2 :
        print("To start the cracker_service, please insert: python3 cracker_service.py <port>")
        exit(0)
    port = sys.argv[1]
    app.run(host = '127.0.0.1', port = int(port))
