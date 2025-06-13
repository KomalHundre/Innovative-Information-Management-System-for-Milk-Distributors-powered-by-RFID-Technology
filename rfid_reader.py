import serial
import time
import requests
from datetime import datetime
import webbrowser

# Configure the serial port
SERIAL_PORT = 'COM5'  # Arduino port
BAUD_RATE = 9600

def setup_serial():
    """Setup serial connection with Arduino"""
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"Connected to {SERIAL_PORT}")
        return ser
    except Exception as e:
        print(f"Error connecting to {SERIAL_PORT}: {str(e)}")
        return None

def read_rfid(ser):
    """Read RFID data from Arduino"""
    try:
        if ser.in_waiting:
            rfid_data = ser.readline().decode('utf-8').strip()
            if rfid_data:
                print(f"\nRaw RFID Data: '{rfid_data}'")
                # Clean up the UID - remove any extra text
                rfid_data = rfid_data.split()[-1] if rfid_data.split() else rfid_data
                rfid_data = ''.join(c for c in rfid_data if c.isalnum())
                print(f"Cleaned UID: '{rfid_data}'")
                print(f"Length of data: {len(rfid_data)}")
                print(f"RFID Read at {datetime.now()}: {rfid_data}")
                return rfid_data
    except Exception as e:
        print(f"Error reading RFID: {str(e)}")
    return None

def send_to_server(rfid_uid):
    """Send RFID UID to Django server"""
    try:
        print(f"\nSending UID to server: '{rfid_uid}'")
        url = 'http://127.0.0.1:8000/dairy/rfid-scan/'
        response = requests.post(url, data={'uid': rfid_uid})
        
        print(f"Server response status: {response.status_code}")
        print(f"Server response content: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"Successfully identified farmer: {data.get('farmer_name')}")
                print(f"Redirecting to: {data.get('redirect_url')}")
                # Open the redirect URL in the default web browser
                webbrowser.open(data.get('redirect_url'))
            else:
                print(f"Error: {data.get('message')}")
        else:
            print(f"Server error: {response.status_code}")
            
    except Exception as e:
        print(f"Error sending data to server: {str(e)}")

def main():
    """Main function to run RFID reader"""
    print("Starting RFID Reader...")
    ser = setup_serial()
    
    if not ser:
        print("Failed to setup serial connection. Exiting...")
        return
    
    print("Waiting for RFID cards...")
    try:
        while True:
            rfid_uid = read_rfid(ser)
            if rfid_uid:
                send_to_server(rfid_uid)
            time.sleep(0.1)  # Small delay to prevent CPU overuse
            
    except KeyboardInterrupt:
        print("\nStopping RFID Reader...")
    finally:
        if ser:
            ser.close()
            print("Serial connection closed")

if __name__ == "__main__":
    main() 