# password_cracker

To start the cracker_service.py, open multiple terminals and on each terminal run:

python3 cracker_service.py <port>

For example, python3 cracker_service.py 5000 (on one terminal) python3 cracker_service.py 5001 (on second terminal) python3 cracker_service.py 5002 (on third terminal)

Note: the port number on each terminal should be different, and have a difference of +1 following a trend such as 5000, 5001, 5002, ... 5011, etc.

To start the client.py, run the following command:

python3 client.py <start_port> <end_port> <md5_password> <max_password_length> <clear_password> <isPrintable>

For example, python3 client.py 5000 5002 ea416ed0759d46a8de58f63a59077499 4 xxxx 0

Note:

When starting the client, we have the option of omitting both <clear_password> and <isPrintable> or having both of them on the terminal. We can't keep only one or another. <clear_password> is just the clear text password of the <md5_password> which is used to determine the average crack time in part4. <isPrintable> is a flag where "1" means the search space is made by printable characters (length 100) and "0" means the search space is made by ascii lowercase characters (length 26). If omitting both <clear_password> and <isPrintable>, the default search space is formed by printable characters.
After we start the service, we should know the range of the port for <start_port> and <end_port>.
