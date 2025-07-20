import os
import time
import serial
import sys
import requests
from datetime import datetime


# EDIT WEBSITE VALUE 0-->100
website_value = 100

# suppress TensorFlow C++ logs if loaded
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
# suppress ChromeDriver logs
os.environ['GLOG_minloglevel'] = '2'

URL = "https://farthole.butthole.exchange/"
now = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
print("Starting Script: ", now)
def connect_to_arduino():
    """
    Connect to the Arduino on a fixed serial port (default /dev/ttyACM0),
    or override with ARDUINO_PORT env var. Prints clear instructions on permission errors.
    """
    SERIAL_PORT = os.getenv('ARDUINO_PORT', '/dev/ttyACM0')
    BAUD_RATE   = 9600

    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"Connected to Arduino on {SERIAL_PORT}")
        # give the board a moment to reset
        time.sleep(2)
        return ser

    except serial.SerialException as e:
        err = str(e).lower()
        if 'permission' in err or 'access denied' in err:
            print(f"Permission denied opening {SERIAL_PORT}.")
            print("On Linux: add your user to the dialout group and reboot:")
            print("  sudo usermod -a -G dialout $USER && reboot")
        else:
            print(f"Error connecting to Arduino on {SERIAL_PORT}: {e}")
        sys.exit(1)

def read_arduino_output(ser):
    """Drain and print any incoming data from the Arduino safely."""
    try:
        while ser.in_waiting:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                print(f"Arduino: {line}")
    except OSError:
        # skip if port not ready or was closed
        pass

def check_need_to_fart():
    """
    Checks the backend API for the needToFart flag.
    Returns ("fart", 1) if needToFart is True, else ("0", 0).
    """
    try:
        response = requests.get("https://farthole.fly.dev/api/stats", timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Check if needToFart is True
        need_to_fart = data.get("needToFart", True)
        
        if need_to_fart:
            print("needToFart flag is True - time to fart!")
            return "fart", 1
        else:
            return "0", 0
            
    except requests.RequestException as e:
        print(f"Error checking API: {e}")
        return "0", 0
    except (KeyError, ValueError) as e:
        print(f"Error parsing API response: {e}")
        return "0", 0

if __name__ == "__main__":
    print("Starting farthole monitor using API...")
    
    try:
        # Poll loop - check API every 2 seconds
        while True:
            value, matched = check_need_to_fart()
            now = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
            
            if matched == 1:
                # needToFart is True - time to fart!
                ser = connect_to_arduino()
                print(f"Commencing Fart at {now}.")
                ser.write(b"d\n")
                ser.flush()
                read_arduino_output(ser)
                print("Sent command: 'd'")
                ser.close()
                
                # After farting, toggle the backend flag to reset it
                try:
                    reset_response = requests.post("https://farthole.fly.dev/api/stats/toggleFart", timeout=5)
                    reset_response.raise_for_status()
                    print("Successfully reset needToFart flag")
                except requests.RequestException as e:
                    print(f"Error resetting needToFart flag: {e}")
                
                time.sleep(9)
            else:
                time.sleep(5)  # Check every 2 seconds
    except KeyboardInterrupt:
        print("\nShutting down farthole monitor...")
    except Exception as e:
        print(f"Unexpected error: {e}")
