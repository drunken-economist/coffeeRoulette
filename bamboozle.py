#!/usr/bin/python3

import configparser
from datetime import datetime
import json
import pymysql
import requests

config = configparser.ConfigParser()
config.read('config.ini')

#Bamboo API docs: https://www.bamboohr.com/api/documentation/
bamboo_api_key = config['bamboo']['api_key']
bamboo_subdomain = config['bamboo']['subdomain']
bamboo_base_url = 'https://' + bamboo_api_key + ':x@api.bamboohr.com/api/gateway.php/' + bamboo_subdomain + '/v1/employees/'
bamboo_headers = {'Accept': 'application/json'}

#MySQL config
mysql_username = config['mysql']['username']
mysql_password = config['mysql']['password']
mysql_database = config['mysql']['database']
db = pymysql.connect('localhost', mysql_username, mysql_password, mysql_database)

def request_employee(employee_id):
	payload = {'fields': 'displayName,CustomRedditUserName,workEmail,hireDate,jobTitle,location,department,division'}
	request_url = bamboo_base_url + str(employee_id)
	r = requests.get(request_url, headers=bamboo_headers, params=payload)
	employee_data = json.loads(r.text)
	employee_info = {}
	employee_info['bamboo_id'] = employee_data.get('id', 0)
	employee_info['name'] = employee_data.get('displayName', None)
	employee_info['reddit_username'] = employee_data.get('CustomRedditUserName', None)
	employee_info['title'] = employee_data.get('jobTitle', None)
	employee_info['location'] = employee_data.get('location', None)
	employee_info['department'] = employee_data.get('department', None)
	employee_info['division'] = employee_data.get('division', None)
	employee_info['tenure'] = (datetime.today() - datetime.strptime(employee_data.get('hireDate', '2005-07-12'), '%Y-%m-%d')).days
	return employee_info

def request_directory():
	request_url = bamboo_base_url + 'directory'
	r = requests.get(request_url, headers=bamboo_headers)
	response = json.loads(r.text)
	directory = []
	for employee in response['employees']:
		directory.append(employee['id'])
	return directory

def populate_database(directory_ids):
	cursor = db.cursor()
	try:
		cursor.execute('''
		DROP TABLE IF EXISTS employees''') 
		cursor.execute('''
		CREATE TABLE employees (id VARCHAR(12)
		, name VARCHAR(50)
		, reddit_username VARCHAR(25)
		, title VARCHAR(50)
		, LOCATION VARCHAR(30)
		, department VARCHAR(50)
		, division VARCHAR(50)
		, tenure INT)''')
		db.commit()
		print('drop/create success')
	except:
		print('error in drop/create, rolling back')
		db.rollback()
	for this_id in directory_ids:
		employee_info = request_employee(this_id)
		print(employee_info)
		query = '''INSERT INTO employees
			(id, 
			name, 
			reddit_username, 
			title, 
			location, 
			department, division, 
			tenure)
			VALUES(%d, "%s", "%s", "%s", "%s", "%s", "%s", %d)''' % (
				int(employee_info['bamboo_id']), 
				employee_info['name'], 
				employee_info['reddit_username'],  
				employee_info['title'], 
				employee_info['location'], 
				employee_info['department'], 
				employee_info['division'], 
				int(employee_info['tenure']))
		try:	
			cursor.execute(query)
			print(employee_info['name'] + ' written to db')
			db.commit()
		except:
			db.rollback()
			print('Error writing ' + employee_info['name'])