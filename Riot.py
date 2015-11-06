import requests
import Riot_Constants as Consts

class RiotAPI(object):

	def __init__(self, api_key, region=Consts.REGIONS['North_America'], global_proxy=Consts.REGIONS['Global']):
		self.api_key = api_key
		self.region = region
		self.global_proxy = global_proxy

	def _request(self, api_url, params={}):
		args = {'champData' : 'spells',
		'api_key': self.api_key}
		for key,value in params.items():
			if key not in args:
				args[key] = value
		response=requests.get(
			Consts.URL['base'].format(
				proxy=self.global_proxy,
				region=self.region,
				url=api_url
			),
			params=args
		)
		return response.json()

	def get_all_abilities(self):
		api_url = Consts.URL['lol_static_data'].format(
			version=Consts.API_VERSIONS['static_data']
		)
		return self._request(api_url)
