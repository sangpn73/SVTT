import threading
import Queue
import csv	
import requests
import sqlite3
import ssl
from detection import *

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE	

### Defines
NUM_SPIDERS = 10
q = Queue.Queue()
apps = read_clues()
i = 0
urls = []
data = {}

### read top-1m urls
with open('top-10.csv', 'r') as csv_file:
	csv_reader = csv.reader(csv_file)
	for line in csv_reader:
		url = line[1]
		urls.append(url)

### Functions
def create_jobs():
	for url in urls:
		q.put(url)
	q.join()

# crawl the next url
def work():
    while True:
        url = q.get()
        spider(url)
        q.task_done()

# Create spider threads (will be terminated when main exits)
def create_spiders():
    for x in range(NUM_SPIDERS):
        t = threading.Thread(target=work)
        t.daemon = True
        t.start()

# Spider definition
def spider(url):
	hurl = "http://" + url
	print(hurl)
	try:		
		req = requests.get(hurl, timeout=3)
		try:
			wsv = req.headers['server']
			ap = check_header(wsv, apps)
			print(ap)
			if data.get(ap) != None:
				data[ap] = data[ap] + 1
			else:
				data[ap] = 1
		except:
			print("Unable to retrive server information from request.headers")
	except:
		print("Site is unreachable. Too bad!!")


### Main
create_spiders()
create_jobs()
print(data)
#conn.commit()

### SQLite
conn = sqlite3.connect('spider.splite')
cur = conn.cursor()

cur.execute('''CREATE TABLE IF NOT EXISTS WebServer
	(app TEXT UNIQUE, num INTEGER)''')

for key, value in data.iteritems():
	cur.execute('INSERT OR IGNORE INTO WebServer (app, num) VALUES (?, ?)', (key, value))

conn.commit()