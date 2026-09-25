import requests

with open('tokens/catapi.txt', 'r') as f:
	token = f.read()
headers = {"x-api-key": token}
params = {"limit": 1, "order": "RAND"}


def get_cat() -> str:
	"""
	:return: cat image url 
	"""
	response = requests.get("https://api.thecatapi.com/v1/images/search", headers=headers, params=params)
	cat_url = response.json()[0]["url"]
	return cat_url


def get_frog() -> str:
	"""
	:return: frog image url
	"""
	response = requests.get("https://frogs.media/api/random")
	frog_url = response.json()["url"]
	return frog_url


pass
