#!/usr/bin/env python

#This script establishes the public IP Address.
#It compares the IP to the stored IP address,
#if they differ the new IP is archived and an 
#email sent with the new IP address.

import sys
import csv
import time
import os
from smtplib import SMTP_SSL as SMTP    #This invokes the secure SMTP protocol (port 465, uses SSL)
from email.MIMEText import MIMEText     #For email
from requests import get		#Only additional package required

### Debug ###
debug = 0		#Give verbose output
force_email = 0		#Forces write to file & Email even if IP address not changed

### SMTP SETTINGS ###
SMTPserver = 'YOUR_SMTP SERVER'
sender =     'YOUR_EMAIL_ADDRESS_TO_SEND_FROM'
USERNAME = "YOUR_EMAIL_ADDRESS_TO_SEND_FROM"
PASSWORD = "YOUR_EMAIL_PASSWORD"
destination = ['EMAIL_ADDRESS_TO_SEND_UPDATES_TO']

### Program Variables ###
text_subtype = 'plain'
content=""
subject="New IP Address"
file_location = '/home/pi/ip_check/ip.csv'
archived_ip = "0.0.0.0"
current_ip = "0.0.0.0"

# Initialise the system and start the main loop
def main():
	check_file_exists() 	#Ensures we have a file to write to.
	get_archived_ip()	#Gets the last recorded IP Address	
	get_current_ip()	#Gets the current IP Address
	compare_ip()

def check_file_exists():
	if not os.path.isfile(file_location):
		try:
			print "File doesn't exist so creating it"
        		with open(file_location, 'a') as csvfile:
            			logfile = csv.writer(csvfile, delimiter=',')
            			logfile.writerow(["Date", "Time", "Public IP"])
			get_current_ip()
			update_ip_file()
			send_email()
			print "File Created, Updated and Email Sent"

		except:
			print "Issue writing to file"
        		pass      		 		

def get_archived_ip():
	global archived_ip
	with open(file_location, 'rb') as csvfile:
		logfile = csv.reader(csvfile, delimiter=',')
		for row in logfile:
			archived_ip = row[2]
		
		if debug == 1:
			print 'My archived public IP address is:', archived_ip

def get_current_ip():
	global current_ip
	current_ip = get('http://api.ipify.org').text

	if debug == 1:
		print 'My public IP address is:', current_ip

def compare_ip():
	if str(archived_ip) != str(current_ip) and (len(current_ip) < 100 ):
		if debug == 1:
			print "IP Address has changed"		
		update_ip_file()
		send_email()
	else:
		if debug == 1:
			print "IP Address has not changed"	

def update_ip_file():
	try:
        	with open(file_location, 'a') as csvfile:
            		logfile = csv.writer(csvfile, delimiter=',')
			logfile.writerow([(time.strftime("%d/%m/%Y")), (time.strftime("%H:%M:%S")), current_ip])
    	except:    
    		pass 

def send_email():
	print "About to send email"
        try:
		content = "Current IP: " + str(current_ip)
		msg = MIMEText(content, text_subtype)
                msg['Subject'] = "New IP address!"
                msg['From'] = sender #some SMTP servers will do this automatically, not all.
		
		if debug == 1:
			print msg.as_string()

                conn = SMTP(SMTPserver)
                conn.set_debuglevel(False)
                conn.login(USERNAME, PASSWORD)

                try:
                        conn.sendmail(sender, destination, msg.as_string())
                finally:
                        print "Email Sent"                      
                        conn.close()
        except Exception, exc:
                sys.exit( "mail failed; %s" % str(exc) ) #give a error message

if __name__ == "__main__":
    main()
