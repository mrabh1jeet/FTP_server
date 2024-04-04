import socket
import os
import ssl

HOST = '10.30.203.130'#'192.168.138.21'  # Server IP address
PORT = 2126

# SSL context creation
ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain(certfile="server.crt", keyfile="server.key")

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind((HOST, PORT))
serverSocket.listen()

print(f'Server listening on {HOST}:{PORT}')

while True:
    conn, addr = serverSocket.accept()
    print(f'Connected with: {addr}')

    # Wrap the connection with SSL
    ssl_conn = ssl_context.wrap_socket(conn, server_side=True)

    try:
        while True:
            command = ssl_conn.recv(1024).decode()
            print(f'Received command: {command}')

            if command.lower() == 'quit':
                exit()
            elif command.lower() == 'list':
                file_list = '\n'.join(os.listdir())
                ssl_conn.sendall(file_list.encode())
            elif command.lower().startswith('dwld'):
                filename = command[5:].strip()
                if filename in os.listdir():
                    with open(filename, 'rb') as file:
                        file_data = file.read()
                    ssl_conn.sendall(file_data)
                else:
                    ssl_conn.sendall(f'File "{filename}" not found'.encode())
            elif command.lower().startswith('upload'):
                filename = command[7:].strip()
                file_data = ssl_conn.recv(1024)
                with open(filename, 'wb') as file:
                    file.write(file_data)
                ssl_conn.sendall(f'File "{filename}" uploaded successfully'.encode())
            else:
                ssl_conn.sendall('Invalid command'.encode())

    finally:
        ssl_conn.close()

serverSocket.close()
