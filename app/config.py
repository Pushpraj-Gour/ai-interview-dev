from pydantic_settings import BaseSettings
import os

class Keys(BaseSettings):

	open_router_key: str
	directory: str

	routers: str
	api_prefix: str

	basic_auth_username: str
	basic_auth_password: str


	class Config:
		env_file = ".env"
		env_file_encoding = "utf-8"

	@classmethod
	def is_local(cls):
		return not os.environ.get('K_SERVICE')
	
class Models():

	deepseek: str  = "deepseek/deepseek-r1:free"  # highly rated
	gemini: str = "google/gemini-2.0-pro-exp-02-05:free"  # reliable
	google_gemma: str = "google/gemma-2-9b-it:free"   # low latency
	

keys = Keys()  # type: ignore
model = Models()