import requests
from bs4 import BeautifulSoup

"""
	Facebook 2021 Leak Search
	Author: @curosim

	About the script:
	I must admit it looks a little too complicated for what it does. But keep in mind the script was written for interactive usage.
	The captcha on the website is lovely - because of that and out of respect for the service operator, it's implemented in the script instead of solved automatically.
"""


# CONFIG #################
onion_service_address =
tor_socks_proxy_port = 9050
onion_service = {
	'url':'4wbwa6vcpvcr3vvf4qkhppgy56urmjcj2vagu2iqgp3z656xcmfdbiqd.onion',
	# To find the captcha box, we search the HTML for the style attribute with following content.
	'captcha_style':'border: 1px solid black;display: inline-block;margin: 0px; padding:0px;'
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
			print("[*] Captcha correct!")
			# Here we extract the ID from the response header
			self.authentication_id = resp.headers['Location'].split('?s=')[1]
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

	def search():
		# TODO: Implement actual search...
		pass


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
	print("IMPORTANT NOTICE:")
	print("This script is simply a CLI wrapper for the following TOR hidden service:")
	print(onion_service['url'])
	print("The author of the script has no affiliation with the operator of the hidden service.")
	print()

def main():
	banner()
	fbls = FacebookLeakSearch(onion_service['url'])
	print('[!] To use the service, you have to solve a captcha first.')
	fbls.ask_for_captcha_solution()
	print('[*] Authentication ID: %s' % str(fbls.authentication_id))
	fbls.search()


if __name__ == '__main__':
	main()