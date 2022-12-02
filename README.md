# FBLS - facebook-leak-search
Simple Python wrapper to query the Facebook 2021 Data Breach Leak Onion Service.

**Onion Service:**
```
4wbwa6vcpvcr3vvf4qkhppgy56urmjcj2vagu2iqgp3z656xcmfdbiqd.onion
```
***Info**: I dont know who runs the hidden service nor am I affiliated in any way. Query it with care.*

### Installation:
```
git clone https://github.com/curosim/facebook-leak-search
```

### Usage:

Simply run the script in the command line.
It's interactive, no parameters needed.

```
python fb-leak-search.py
```






###### Additional Features which could be implemented in the future:
- Implement Key Rotation for Authentication ID
- Implement way to show how many search queries are left (it's in the page source)
- Automatic re-auth of captcha after 50 queries used
- Possibility of solving multiple captchas at first and key rotation afterwards
- Possibility of processing lists
- Implement Facebook Profile URL to ID converter

