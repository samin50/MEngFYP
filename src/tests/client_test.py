import socket
import pickle
import time
from src.vision.vsrc.constants import SERVER_PORT, SERVERNAME

def vision_client():
    """
    Vision client function
    """
    # Create the server
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        connected = False
        while not connected:
            try:
                print(f"Connecting to server {SERVERNAME}:{SERVER_PORT}")
                client.connect((SERVERNAME, SERVER_PORT))
                connected = True
            except Exception as e:
                print("Error: ", e)
                print("Trying to connect again...")
                time.sleep(1)
        print("Connected to server")
        # Send data to the server
        data = {"image": "test.jpg"}
        data = pickle.dumps(data)
        client.send(data)
        # Get the response from the server
        response = client.recv(1024)
        response = pickle.loads(response)
        print("Response from server: ", response)

if __name__ == "__main__":
    print("Starting vision client...")
    vision_client()
