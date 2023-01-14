Coen 366 Project
By Jason Hillinger and Siddhesh Mishra

How to:
    To run the program do the following steps:
        1. run in terminal: pip install pyinputplus
        2. Make sure to have 2 terminals (we suggest using split terminals)
        3. On one of the terminal, run this command in the FileTransferService directory: python3 Server/server.py 12000 1
        4. On the second terminal run this command in the FileTransferService directory: cd Client
        5. Now that you are in the Client directory run: python3 client.py localhost 12000 0
        6. You should now have a server and client running, you can now make requests using the client terminal (the second terminal)

    To test the program, there is a Files folder included for both Client and Server folders.
    This means there is no need for a Test folder.
    Now to test the program do the following:
        1. On the client terminal enter a commad such as: help
        2. you should see a response from the server telling you the possible Commands
        3. Now you can run any of the given commands using the files in either Files folders.

