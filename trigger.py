import requests
import sys
import time
from datetime import datetime

BACKEND_URL = "http://localhost:8000/api/v1/telemetry"

def send_payload(temp, hum, gas, scenario_name, repeat=3):
    # Loop to hold the anomaly state long enough for the dashboard to catch it
    for _ in range(repeat):
        payload = {
            "sensor_id": "SENS-ShelfA1",
            "location": "Shelf A1",
            "timestamp": datetime.utcnow().isoformat(),
            "temperature": temp,
            "humidity": hum,
            "gas_level": gas
        }
        try:
            response = requests.post(BACKEND_URL, json=payload, timeout=2)
            if response.status_code != 200:
                print(f"[ERROR] Backend returned: {response.status_code}")
        except Exception as e:
            print(f"[ERROR] Connection failed: {e}")
        
        # Wait 1.5 seconds before overriding the simulator again
        time.sleep(1.5)
        
    print(f"[SUCCESS] {scenario_name} injected to Shelf A1 and held for {repeat * 1.5} seconds!")

def main():
    print("\n--- SMARTA Demo Controller ---")
    print("0: Send Normal Data (Reset to safe state)")
    print("1: Trigger High Temperature (Simulate AC Failure)")
    print("2: Trigger High Humidity (Simulate Leak/Ventilation Issue)")
    print("3: Trigger High Methane Gas (Simulate Spoilage/Decay)")
    print("4: Trigger All Critical (Total System Failure)")
    print("q: Quit")
    
    while True:
        choice = input("\nSelect scenario to inject (0-4 or q): ").strip()
        
        if choice == '0':
            send_payload(20.0, 52.0, 0.2, "Normal Data", repeat=1)
        elif choice == '1':
            send_payload(45.0, 52.0, 0.2, "High Temperature Anomaly")
        elif choice == '2':
            send_payload(20.0, 85.0, 0.2, "High Humidity Anomaly")
        elif choice == '3':
            send_payload(20.0, 52.0, 5.8, "High Methane Anomaly")
        elif choice == '4':
            send_payload(45.0, 85.0, 5.8, "Total Failure Anomaly")
        elif choice.lower() == 'q':
            print("Exiting controller...")
            sys.exit()
        else:
            print("Invalid input. Please choose a number from 0 to 4.")

if __name__ == "__main__":
    main()