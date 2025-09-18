import socket

def main():
    print("Logs from your program will appear here.")
    # AF_INET: IPv4 family
    # SOCK_STREAM: using TCP
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # It lets us reuse the same address (ip-address+port) immediately after the
    # program exits
    # It prevents the address already in use error


    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_socket.bind('localhost', 4221)
    server_socket.listen()
    print("Server is listening on port 4221...")

    while True:
        # When a client connects, accept() returns a tuple, a new socket object
        # and the address of the client. 
        connection, address = server_socket.accept()
        print(f"Accepted a new connection from {address}")

if __name__=="__main__":
    main()