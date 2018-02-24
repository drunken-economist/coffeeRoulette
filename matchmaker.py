import configparser
import pymysql

config = configparser.ConfigParser()
config.read('config.ini')

#MySQL config
mysql_username = config['mysql']['username']
mysql_password = config['mysql']['password']
mysql_database = config['mysql']['database']
db = pymysql.connect('localhost', mysql_username, mysql_password, mysql_database)
