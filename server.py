import socket
import threading

def handle_connection(connection):
    print(f"Handling connection in a new thread.")
        
    with connection:
        request_data = connection.recv(1024)
        if not request_data:
            return 
        decoded_request = request_data.decode('utf-8')
        request_lines = decoded_request.split('\r\n')
        print(f"Request Received: \n{decoded_request}")
        request_line = request_lines[0]
        path = request_line.split(' ')[1]

        # Parse headers into a dictionary 
        headers = {}
        for line in request_lines[1:]:
            if line:
                #Everything before the first : goes into key.
                #Everything after the first : goes into value.
                key, value = line.split(": ", 1)
                headers[key.lower()] = value 

        if path =='/':
            http_response = b"HTTP/1.1 200 OK\r\n\r\n"
        elif path.startswith("/echo/"):
            body = path.split('/echo/')[1]
            http_response_str = (
                        f"HTTP/1.1 200 OK\r\n"
                        f"Content-Type: text/plain\r\n"
                        f"Content-Length: {len(body)}\r\n"
                        f"\r\n"
                        f"{body}"
                    )
            http_response = http_response_str.encode()
        elif path == "/user-agent":
            body = headers.get('user-agent', 'Unknown')
            http_response_str = (
                        f"HTTP/1.1 200 OK\r\n"
                        f"Content-Type: text/plain\r\n"
                        f"Content-Length: {len(body)}\r\n"
                        f"\r\n"
                        f"{body}"
                                    
                    )
            http_response = http_response_str.encode()
        else:
            http_response = b"HTTP/1.1 404 Not Found\r\n\r\n"


                
        connection.sendall(http_response)
        print(f"Responded to path {path} and closed connection.")
                

def main():
    print("Logs from your program will appear here.")
    # AF_INET: IPv4 family
    # SOCK_STREAM: using TCP
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # It lets us reuse the same address (ip-address+port) immediately after the
    # program exits
    # It prevents the address already in use error
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('localhost', 4221))
    server_socket.listen()
    print("Server is listening on port 4221...")
    while True:
            # When a client connects, accept() returns a tuple, a new socket object
            # and the address of the client. 
            connection, address = server_socket.accept()
            print(f"Accepted a new connection from {address}")
            # Sending back response to the client
            thread = threading.Thread(target = handle_connection, args=(connection,))
            thread.start()
    

if __name__=="__main__":
    main()