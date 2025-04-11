from app import app
import os
from app.utils.port_finder import find_available_port

if __name__ == "__main__":
    # Try to get port from environment, otherwise find an available one
    try:
        port = int(os.environ.get("PORT", find_available_port()))
    except ValueError:
        port = find_available_port()
    
    print(f"Starting server on port {port}")
    app.run(host="127.0.0.1", port=port) 