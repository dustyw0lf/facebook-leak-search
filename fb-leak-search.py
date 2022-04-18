import requests
from bs4 import BeautifulSoup
from prettytable import PrettyTable

"""
	Facebook 2021 Leak Search
	Author: @curosim

	About the script:
	I must admit it looks a little too complicated for what it does. But keep in mind the script was written for interactive usage.
	The captcha on the website is lovely - because of that and out of respect for the service operator, it's implemented in the script instead of solved automatically.
"""


# CONFIG #################
tor_socks_proxy_port = 9050
onion_service = {
	# URL of the Onion service
	'url':'4wbwa6vcpvcr3vvf4qkhppgy56urmjcj2vagu2iqgp3z656xcmfdbiqd.onion',

	# To find the captcha box, we search the HTML for the style attribute with following content.
	'captcha_style':'border: 1px solid black;display: inline-block;margin: 0px; padding:0px;',
	
	# Text which is shown on the page if a captcha is present
	'captcha_present_text':'fill in captcha!',

	# Results table style attribute content
	'results_table_style':'min-width: 50%'
}
##########################


def get_tor_session():
	""" Returns a requests session with the tor service set as socks proxy.
	"""
	session = requests.session()

	# It's important to use the protocol 'socks5h' in order to enable remote DNS resolving
	session.proxies['http'] = 'socks5h://localhost:9050'.format(tor_socks_proxy_port)
	session.proxies['https'] = 'socks5h://localhost:9050'.format(tor_socks_proxy_port)
	return session

class FacebookLeakSearch():
	authentication_id = None

	def __init__(self, onion_address):
		self.session = get_tor_session()
		self.hidden_service_url = 'http://{0}'.format(onion_address)

	def initial_request(self):
		""" Simply for the first request in order to get the page source for the captcha.
		"""
		resp = self.session.get(self.hidden_service_url)
		return resp.text

	def is_captcha_present(self, source):
		""" Checks if the captcha is present in the HTML source.
		"""
		if onion_service['captcha_present_text'] in source:
			return True
		else:
			return False

	def extract_captcha_from_source(self, source):
		""" The HTML source gets passed and the captcha text + hidden key will be extracted from it.
		"""
		soup = BeautifulSoup(source, 'html.parser')
		captcha_text = soup.find('pre', attrs={'style':onion_service['captcha_style']}).text
		hidden_key = soup.find('input', attrs={'type':'hidden','name':'id'}).get('value')
		return captcha_text, hidden_key

	def solve_captcha(self, captcha_text, hidden_key):
		""" Solve the captcha (Send solution to server).
		"""

		print("[*] Submitting captcha solution '{0}'".format(captcha_text))
		
		data = {
			'captcha': captcha_text,
			'id': hidden_key
		}

		url = self.hidden_service_url+'/captcha'
		resp = self.session.post(url, data=data, allow_redirects=False)

		# If the captcha was correct, we get redirected to another URL
		# The new URL will be the same domain, but with a GET parameter 's' which acts as an identifier that we solved the captcha.
		# All further requests must be made with the s parameter set, otherwise the captcha will show up again.
		if resp.status_code == 302:
			# Here we extract the ID from the response header
			self.authentication_id = resp.headers['Location'].split('?s=')[1]
			print("[*] Captcha correct! (Auth ID: {0})".format(self.authentication_id))
			return True
		else:
			print("[!] The captcha solution was wrong! Try again.")
			return False

	def ask_for_captcha_solution(self, source=None):
		""" Ask the user to solve the captcha.
			It's a recursive function.
		"""

		if source is None: source = self.initial_request()

		captcha_text, hidden_key = self.extract_captcha_from_source(source)
		print(captcha_text)
		captcha_solution = input('[*] Enter the letters: ')
		success = self.solve_captcha(captcha_solution, hidden_key)

		# If the captcha is wrong, call the function again :)
		if success == False: self.ask_for_captcha_solution()

	def ask_for_search_input(self):
		print("[*] Please enter the search criteria (Leave blank if not needed):")
		user_id = input("  > User ID: ")
		first_name = input("  > First Name: ")
		last_name = input("  > Last Name: ")
		phone_number = input("  > Phone Number: ")
		work = input("  > Work: ")
		location = input("  > Location: ")
		#relationship_status = input("[*] Relationship Status: ")
		#gender = input("[*] Gender: ")

		return self.perform_search(user_id, first_name, last_name, phone_number, work, location, relationship_status='*any*', gender='*any*')

	def perform_search(self, user_id, first_name, last_name, phone_number, work, location, relationship_status, gender):
		print("[*] Performing DB search")
		params = {
			's':self.authentication_id,
			'i':user_id, # ID
			'f':first_name, # firstname
			'l':last_name, # lastname
			't':phone_number, # phone number
			'w':work, # work
			'o':location, # location
			'r':relationship_status, # relationship status
			'g':gender  # gender
		}
		url = self.hidden_service_url+'/search'
		resp = self.session.post(url, params=params, allow_redirects=False)
		
		return self.parse_results_table(resp.text)

	def parse_results_table(self, source):

		results = []
		soup = BeautifulSoup(source, 'html.parser')
		
		# get the table with the results
		table_rows = soup.find_all('tr')

		for row in table_rows[1:]:
			tds = row.find_all('td')

			entry = {}
			entry['user_id'] = tds[0].text
			entry['phone_number'] = tds[1].text
			entry['first_name'] = tds[2].text
			entry['last_name'] = tds[3].text
			entry['gender'] = tds[4].text
			entry['relationship_status'] = tds[5].text
			entry['work'] = tds[6].text
			entry['hometown'] = tds[7].text
			entry['location'] = tds[8].text
			entry['country'] = tds[9].text
			results.append(entry)

		print("[*] Success! {0} results have been found!".format(len(results)))

		return results

def banner():
	print(" ________  ______   _____      ______   ")
	print("|_   __  ||_   _ \\ |_   _|   .' ____ \\  ")
	print("  | |_ \\_|  | |_) |  | |     | (___ \\_| ")
	print("  |  _|     |  __'.  | |   _  _.____`.  ")
	print(" _| |_     _| |__) |_| |__/ || \\____) |")
	print("|_____|   |_______/|________| \\______.'")
	print()
	print("Facebook Leak Search - Author: @curosim")
	print()
	"""
	print("IMPORTANT NOTICE:")
	print("This script is simply a CLI wrapper for the following TOR hidden service:")
	print(onion_service['url'])
	print("The author of the script has no affiliation with the operator of the hidden service.")
	print()
	"""

def main():
	banner()
	fbls = FacebookLeakSearch(onion_service['url'])
	print('[!] To use the service, you have to solve a captcha first.')
	fbls.ask_for_captcha_solution()
	results = fbls.ask_for_search_input()

	results_table = PrettyTable()
	results_table.field_names = ["User ID", "Phone", "Name", "Lastname", "Gender", "Work", "Hometown", "Location", "Country"]
	results_table.align = 'l'

	for result in results:
		results_table.add_row(
			[
				result['user_id'],
				result['phone_number'],
				result['first_name'],
				result['last_name'],
				result['gender'],
				result['work'],
				result['hometown'],
				result['location'],
				result['country']
			]
		)


	print(results_table)

	"""
	TODO:
	- Maybe add way to save results to DB for further browsing
	- Implement way to show how many search queries are left (it's in the page source)
	- Automatic re-auth of captcha after 50 queries used
	- Possibility of solving multiple captchas at first and key rotation afterwards
	- Possibility of processing lists
	- Implement Facebook Profile URL to ID converter

	"""


if __name__ == '__main__':
	main()