from app.utils.port_finder import find_available_port
import os
import subprocess

def main():
    # Find an available port
    port = os.environ.get("PORT", find_available_port())
    print(f"Starting gunicorn on port {port}")
    
    # Run gunicorn
    cmd = f"gunicorn wsgi:app -b 127.0.0.1:{port} --log-level debug"
    subprocess.run(cmd, shell=True)

if __name__ == "__main__":
    main() 