import socket
import threading
import sys
import os
import gzip

def handle_connection(connection, directory):
    """
    Handles a client connection, now with a loop to support persistence.
    """
    try:
        # Loop to handle multiple requests on the same connection
        while True:
            request_data = connection.recv(4096)
            if not request_data:
                # If recv returns empty bytes, the client has closed the connection
                print("Client closed the connection.")
                break

            decoded_request = request_data.decode('utf-8', errors='ignore')
            request_lines = decoded_request.split('\r\n')
            
            request_line = request_lines[0]
            method = request_line.split(' ')[0]
            path = request_line.split(' ')[1]
            
            headers = {}
            body_start_index = decoded_request.find('\r\n\r\n')
            header_part = decoded_request[:body_start_index]
            
            for line in header_part.split('\r\n')[1:]:
                if line:
                    key, value = line.split(': ', 1)
                    headers[key.lower()] = value

            if path == "/":
                http_response = b"HTTP/1.1 200 OK\r\n\r\n"
            elif path.startswith("/echo/"):
                body_str = path.split('/echo/')[1]
                response_headers = ["HTTP/1.1 200 OK", "Content-Type: text/plain"]
                
                accept_encoding = headers.get('accept-encoding', '')
                if 'gzip' in [encoding.strip() for encoding in accept_encoding.split(',')]:
                    response_headers.append("Content-Encoding: gzip")
                    compressed_body = gzip.compress(body_str.encode())
                    response_headers.append(f"Content-Length: {len(compressed_body)}")
                    response_headers_str = "\r\n".join(response_headers)
                    http_response = response_headers_str.encode() + b"\r\n\r\n" + compressed_body
                else:
                    response_headers.append(f"Content-Length: {len(body_str)}")
                    response_headers_str = "\r\n".join(response_headers)
                    http_response = (response_headers_str + f"\r\n\r\n{body_str}").encode()

            # ... (other elif routes for /user-agent and /files remain the same) ...
            elif path == "/user-agent":
                body = headers.get('user-agent', 'Unknown')
                http_response_str = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(body)}\r\n\r\n{body}"
                http_response = http_response_str.encode()
            elif path.startswith("/files/"):
                filename = path.split('/files/')[1]
                file_path = os.path.join(directory, filename)
                
                if method == 'GET':
                    try:
                        with open(file_path, 'rb') as f:
                            body = f.read()
                        http_response_str = f"HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\nContent-Length: {len(body)}\r\n\r\n"
                        http_response = http_response_str.encode() + body
                    except FileNotFoundError:
                        http_response = b"HTTP/1.1 404 Not Found\r\n\r\n"
                elif method == 'POST':
                    body_content = decoded_request[body_start_index + 4:]
                    with open(file_path, 'wb') as f:
                        f.write(body_content.encode())
                    http_response = b"HTTP/1.1 201 Created\r\n\r\n"
            else:
                http_response = b"HTTP/1.1 404 Not Found\r\n\r\n"
            
            connection.sendall(http_response)
            print(f"Responded to {method} request for '{path}'. Waiting for next request...")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Ensure the connection is closed when the loop exits
        connection.close()
        print("Connection closed in thread.")


def main():
    print("Logs from your program will appear here!")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('localhost', 4221))
    server_socket.listen()
    print("Server is listening on port 4221...")
    
    directory = ""
    if len(sys.argv) > 2 and sys.argv[1] == '--directory':
        directory = sys.argv[2]
        print(f"Serving and saving files in directory: {directory}")

    while True:
        connection, address = server_socket.accept()
        print(f"Accepted a new connection from {address}")
        thread = threading.Thread(target=handle_connection, args=(connection, directory))
        thread.start()

if __name__ == "__main__":
    main()