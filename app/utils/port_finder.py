import socket

def find_available_port(start_port=8080, max_port=9000):
    """Find an available port starting from start_port up to max_port."""
    for port in range(start_port, max_port):
        try:
            # Try to create a socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('127.0.0.1', port))
            sock.close()
            return port
        except OSError:
            continue
    raise RuntimeError(f"No available ports found between {start_port} and {max_port}") 