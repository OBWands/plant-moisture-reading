import board
import csv
import sendemail
import os
import time
from adafruit_seesaw.seesaw import Seesaw
from configparser import ConfigParser

filepath = "/home/pi/plant-moisture-reading/Pothos2.csv"
parser = ConfigParser()
parser.read('/home/pi/plant-moisture-reading/dev.ini')
alert_email = parser.get('email_subject', 'status_alert')
send_email = sendemail.send_alert_email

if not os.path.isfile(filepath):
    # Create CSV file
    headers = ['Local Time', 
               'Moisture', 
               'Temperature', 
               'Watering Needed']
    with open(filepath, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(headers)
    print('csv created')

# Set datetime to yyyy-mm-dd hh:mm
datetime_string = time.strftime("%G-%m-%d %R")
print(f'Local Time: {datetime_string}')

i2c_bus = board.I2C()
ss = Seesaw(i2c_bus, addr=0x36)
number_of_sensor_readings = 20

# Read moisture level through capacitive touch pad
moisture_list = []
for i in range (number_of_sensor_readings):
    moisture_list.append(ss.moisture_read())
    print('Moisture reading taken')
    time.sleep(.5)    
moisture = round(sum(moisture_list)/len(moisture_list), 2)
print(f'Moisture: {moisture}') 

# Read temperature from the temperature sensor
temp_list = []
for i in range (number_of_sensor_readings):
    temp_list.append(ss.get_temp())
    print('Temperature reading taken')
    time.sleep(.5)    
temp = round(sum(temp_list)/len(temp_list),2)
print(f'Temp: {temp}')

if moisture < 955:
    watering_needed = 1
else:
    watering_needed = 0
print(f'Watering Needed: {watering_needed}')

rows = [datetime_string, 
        moisture, 
        temp, 
        watering_needed]
with open(filepath, 'a') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(rows)


def watering_alert_email_check(number_of_rows, file_to_open):
    """
    Check the last "number_of_rows" to see if there have been prior alerts
    If there's no alert in the past number_of_rows, send an alert email
    """
    print("Starting function")
    # List to store prior watering needed variables
    prior_watering_list = []
    for i in range(-1, number_of_rows, -1):
        with open(file_to_open, "r") as f:
            last_line = f.read().splitlines()[i]
            last_line_list = last_line.split(",")
            prior_watering_list.append(int(last_line_list[3]))
    print(prior_watering_list)
    print(
        f"Number of times readings were low: {sum(prior_watering_list)}"
        )
        
    # Checking multiple lines reduces sensor reading fluctuation errors
    if sum(prior_watering_list) == 1:        
        send_email(alert_email)
        print('Alert Email Sent')
    else:
        print('All Good')
    print("Function Used")


file = open(filepath)
reader = csv.reader(file)
row_count = len(list(reader))
# Make row count negative to use in function
neg_row_count = row_count * -1
rows_to_count = 12  # Needs to be greater than 2, 1 row = 15 min
rows_to_count_value = int((rows_to_count + 2) * -1)

if watering_needed == 1:    
    if row_count >= rows_to_count:
        print("Using first IF")
        watering_alert_email_check(rows_to_count_value, filepath)
    # Use all lines if there is less than # of rows_to_count variable
    elif row_count > 2:
        print("Using second IF")
        watering_alert_email_check(neg_row_count, filepath)
    # Used when this is the first recording of data
    elif row_count == 2:
        print("Using third IF")
        send_email(alert_email)
        print('Alert Email Sent')    
else:
    print('All Good')

print(
f'Local Time: {datetime_string}, Moisture: {moisture}, Temp: {temp}, '
f'Watering Needed: {watering_needed}'
)
print('Entry Complete')
