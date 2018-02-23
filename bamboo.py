import configparser
from datetime import datetime
import json
import requests

config = configparser.ConfigParser()
config.read('config.ini')

#Bamboo API docs: https://www.bamboohr.com/api/documentation/
bamboo_api_key = config['bamboo']['api_key']
bamboo_subdomain = config['bamboo']['subdomain']
bamboo_base_url = 'https://' + bamboo_api_key + ':x@api.bamboohr.com/api/gateway.php/' + bamboo_subdomain + '/v1/employees/'
bamboo_headers = {'Accept': 'application/json'}

def request_employee(id):
	payload = {'fields': 'displayName,CustomRedditUserName,workEmail,hireDate,jobTitle,location,department,division,photoUrl'}
	request_url = bamboo_base_url + id
	r = requests.get(request_url, headers=bamboo_headers, params=payload)
	employee_data = json.loads(r.text)
	employee_info = {}
	employee_info['id'] = employee_data['id']
	employee_info['name'] = employee_data['displayName']
	employee_info['username'] = employee_data['CustomRedditUserName']
	employee_info['tenure'] = (datetime.today() - datetime.strptime(employee_data['hireDate'], '%Y-%m-%d')).days
	employee_info['title'] = employee_data['jobTitle']
	employee_info['location'] = employee_data['location']
	employee_info['department'] = employee_data['department']
	employee_info['division'] = employee_data['division']
	employee_info['photo'] = employee_data['photoUrl']
	return employee_info

def request_directory():
	request_url = bamboo_base_url + 'directory'
	r = requests.get(request_url, headers=bamboo_headers)
	directory = json.loads(r.text)
	directory_ids = []
	for employee in directory['employees']:
		directory_ids.append(employee['id'])
	return directory_ids