import RPi.GPIO as GPIO
import Adafruit_DHT
import time
import requests
import tkinter as tk
from threading import Thread

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Motion sensor
pir_sensor = 18
GPIO.setup(pir_sensor, GPIO.IN)

# Moisture sensor
moisture_sensor = 17
GPIO.setup(moisture_sensor, GPIO.IN)

# Temperature sensor
temperature_sensor = 27
GPIO.setup(temperature_sensor, GPIO.IN)

# Webhook for notification
WEBHOOK_URL = "https://maker.ifttt.com/trigger/pet_status/json/with/key/b7Aw7HvE4D1amqbemrfXS6"

def send_notification(temperature_threshold):
    while True:
        # Get the motion and water bowl status
        motion_detected = GPIO.input(pir_sensor)
        water_detected = GPIO.input(moisture_sensor)
       
        # If there is no water, instantly send notification to user
        if water_detected == 0:
            print("No water detected!")
            response = requests.post(WEBHOOK_URL, json={"Water Status": "Empty"})
       
        # If the pet is in the room
        if motion_detected == 1:
            
            # 10 seconds Fault tolerance check
            time.sleep(10)
            motion_detected = GPIO.input(pir_sensor)
            
            # If motion is detected again
            if motion_detected == 1:
                
                print("Motion detected.")
                
                # Get the humidity and temperature reading
                humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, temperature_sensor)
               
                # If the water status has changed to zero from prior check
                if water_detected == 0:
                    water_output = "Empty"
                    # Send notification to user if water is empty and pet is in the room
                    response = requests.post(WEBHOOK_URL, json={"Water Status": "Empty"})
                
                # Water is present on the screen
                else:
                    water_output = "Water Present"
               
                # If the temperature reading is higher than the threshold 
                # Send the status of water, temperature, and humidity to notify user
                if temperature > temperature_threshold:
                    response = requests.post(WEBHOOK_URL, json={"Water Status": water_output, "Temperature": temperature, "Humidity": humidity})
           
        # How often readings occur to scan room
        time.sleep(10)

# Function for user input GUI
def on_submit():
    temperature_threshold = float(entry.get())
    notification_thread = Thread(target=send_notification, args=(temperature_threshold,))
    notification_thread.start()

# Create the GUI
root = tk.Tk()
root.title("Temperature Notification")
root.geometry("300x100")

label = tk.Label(root, text="Enter temperature threshold:")
label.pack()

entry = tk.Entry(root)
entry.pack()

submit_btn = tk.Button(root, text="Submit", command=on_submit)
submit_btn.pack()

root.mainloop()
