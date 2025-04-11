import socket
import subprocess
import sys
import signal
import os
from time import sleep

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def find_available_port(start_port=8081, max_attempts=20):
    port = start_port
    while port < start_port + max_attempts:
        if not is_port_in_use(port):
            return port
        port += 1
    return None

def cleanup_existing_processes():
    try:
        subprocess.run(['pkill', '-f', 'gunicorn'], check=False)
        sleep(1)  # Give processes time to cleanup
    except Exception as e:
        print(f"Warning: Could not clean up existing processes: {e}")

def run_server():
    # Clean up any existing gunicorn processes
    cleanup_existing_processes()
    
    port = find_available_port()
    if not port:
        print("Could not find an available port after 20 attempts")
        sys.exit(1)

    print(f"Starting server on port {port}")
    cmd = [
        "gunicorn",
        "wsgi:app",
        f"--bind=127.0.0.1:{port}",
        "--workers=1",
        "--threads=1",
        "--timeout=120",
        "--log-level=debug",
        "--access-logfile=-",
        "--error-logfile=-"
    ]
    
    process = None
    try:
        process = subprocess.Popen(cmd)
        print(f"Server running with PID: {process.pid}")
        process.wait()
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
    finally:
        if process:
            try:
                # Send SIGTERM to the process group
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                process.wait(timeout=5)  # Wait up to 5 seconds for graceful shutdown
            except (subprocess.TimeoutExpired, ProcessLookupError):
                # If process doesn't shut down gracefully, force kill it
                try:
                    process.kill()
                except ProcessLookupError:
                    pass
        cleanup_existing_processes()
        print("Server shutdown complete")
    return 0

if __name__ == "__main__":
    sys.exit(run_server()) 