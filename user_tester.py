from urllib import urlencode
from httplib2 import Http
import json
import sys
import base64


print "Running Testcases"
address = 'http://localhost:5000'


 #TEST 1 TRY TO MAKE A NEW USER
try:
	url = address + '/users'
 	h = Http()
 	data = dict(username = "Rishabh", password = "Rishabh")
 	data = json.dumps(data)
 	resp, content = h.request(url,'POST', body = data, headers = {"Content-Type": "application/json"})
	if resp['status'] != '201' and resp['status'] != '200':
 		raise Exception('Received an unsuccessful status code of %s' % resp['status'])
except Exception as err:
	print "Test 1 FAILED: Could not make a new user"
	print err.args
	sys.exit()
else:
	print "Test 1 PASS: Succesfully made a new user or user already exists"

#TEST 2 TRY TO ACCESS '/api/resources' WITH WRONG CREDENTIALS
try:
	h = Http()
	h.add_credentials('ABCD','ABCD')
	url = address + '/api/resource'
	data = dict(username = "ABCD", password = "ABCD")
	resp, content = h.request(url,'GET', urlencode(data))
	if resp['status'] == '200':
		raise Exception("Security Flaw: able to log in with invalid credentials")
except Exception as err:
	print "Test 2 FAILED"
	print err.args
	sys.exit()
else:
	print "Test 2 PASS: Unable to access with invalid credentials"


#TEST 3 TRY TO ACCESS '/api/resources' WITH CORRECT CREDENTIALS
try:
	h = Http()
	h.add_credentials("Rishabh", "Rishabh")
	url = address + '/api/resource'
	resp, content = h.request(url,'GET')
	if resp['status'] != '200':
		raise Exception("Unable to access /api/resouce with valid credentials")
except Exception as err:
	print "Test 3 FAILED"
	print err.args
	sys.exit()
else:
	print "Test 3 PASS: Logged in User can view /api/resource"


#TEST 4 TRY TO ACCESS '/home' WHICH IS RATE LIMITED TO SHOW EFFECT OF RATE LIMITING 
try:
	h = Http()
	h.add_credentials("Rishabh", "Rishabh")
	url = address + '/home'
	for i in range(0,10):
		resp, content = h.request(url,'GET')
		if resp['status'] != '200':
			raise Exception("Unable to access /home with valid credentials")
except Exception as err:
	print "Test 4 PASS: User got Rate Limited"
else:
	print "Test 4 FAILED: Logged in User can view /home without being Rate Limited"
	sys.exit()


#TEST 5 TRY TO ACCESS '/api/users/1' WHICH IS NOT RATE LIMITED TO SHOW EFFECT OF RATE LIMITING 
try:
	h = Http()
	h.add_credentials("Rishabh", "Rishabh")
	url = address + '/api/users/1'
	for i in range(0,20):
		resp, content = h.request(url,'GET')
		if resp['status'] != '200':
			raise Exception("Unable to access /home with valid credentials")
except Exception as err:
	print "Test 5 FAILED. User should have been able to see this page as many times as he want"
else:
	print "Test 5 PASS: No Rate Limit on this page"
	sys.exit()	