import json 
import requests
import urllib

FB_APP_ID = '461945903879851'
app_url = 'https://graph.facebook.com/{0}'.format(FB_APP_ID)
FB_APP_NAME = json.loads(requests.get(app_url).content).get('name')
FB_APP_SECRET = 'ca5e0bc12c047230c2c801d68acca4b7'
requests = requests.session()
if __name__ == "__main__":
	print FB_APP_NAME