import requests
import json
import time
import threading
import socket

# Application ID (found in Glowmarkt web interface)
APPLICATION_ID = "b0f1b774-a586-4f72-9edd-27ead8aa7a8d"

# Your Glowmarkt resource ID
RESOURCE_ID = "YOUR RESOURCE"

# Glowmarkt API endpoints
API_URL = f"https://api.glowmarkt.com/api/v0-1/resource/{RESOURCE_ID}/current"
TOKEN_URL = "https://api.glowmarkt.com/api/v0-1/auth"

# Authentication details
USERNAME = "BRIGHT USERNAME"
PASSWORD = "BRIGHT PASSWORD"

# Loxone Miniserver details
LOXONE_IP = "LOXONE MINISERVER IP"  # Replace with your Loxone Miniserver IP
LOXONE_PORT = UDP PORT  # Virtual Input UDP port

# Store the access token and current consumption data globally
access_token = None
current_consumption = None

# Function to fetch a new token
def fetch_token():
    global access_token
    headers = {
        "Content-Type": "application/json",
        "applicationid": APPLICATION_ID
    }
    body = {
        "username": USERNAME,
        "password": PASSWORD
    }
    response = requests.post(TOKEN_URL, headers=headers, json=body)
    if response.status_code == 200:
        access_token = response.json().get("token")
        print("Fetched new token")
    else:
        print(f"Failed to fetch token. Status code: {response.status_code}")
        access_token = None

# Function to get current consumption
def get_current_consumption():
    global access_token, current_consumption
    if not access_token:
        fetch_token()
    
    if not access_token:
        return "Error fetching token"
    
    headers = {
        "applicationId": APPLICATION_ID,
        "token": access_token,
        "Content-Type": "application/json"
    }
    response = requests.get(API_URL, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if "data" in data and len(data["data"]) > 0 and len(data["data"][0]) > 1:
            current_consumption = str(data["data"][0][1])
    elif response.status_code == 401:  # Unauthorized, token might have expired
        print("Token expired, fetching a new one")
        fetch_token()
        get_current_consumption()
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        current_consumption = "Error fetching data"

def send_to_loxone(data):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.sendto(data.encode(), (LOXONE_IP, LOXONE_PORT))
        print(f"Sent data to Loxone: {data}")

def fetch_and_send_data():
    while True:
        get_current_consumption()
        if current_consumption:
            send_to_loxone(current_consumption)
        time.sleep(2) # Check every 2 seconds, this can be changed

# Start the data fetching and sending thread
data_fetch_thread = threading.Thread(target=fetch_and_send_data)
data_fetch_thread.daemon = True
data_fetch_thread.start()

# Keep the main thread alive
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Stopping the script.")
