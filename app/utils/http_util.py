import aiohttp
import logging
import asyncio
import sys


# This is hardlink between kntr/app and kntr_be/app

import asyncio
import aiohttp
from tenacity import retry, TryAgain, wait_exponential, \
	wait_random, before_sleep_log, stop_after_attempt,\
	retry_if_exception_type

import logging
logger = logging.getLogger(__name__)


class HTTPUtil:
	def __init__(self, timeout=300):
		self.client = None
		self.timeout = timeout

	def __del__(self):
		"""
		https://github.com/aio-libs/aioredis-py/blob/ff5a8fe068ebda837d14c3b3777a6182e610854a/aioredis/client.py#L1012

		We close async resources by first checking if the event loop is running,
		and creating a new one if it isn't.
		"""

		if self.client is None:
			return

		try:
			loop = asyncio.get_event_loop()
			if loop.is_running():
				print('loop running')
				loop.create_task(self.client.close())
				
				# print('loop running 1.5')
				# loop.run_until_complete(t)

				# print('loop running 2')
				# loop.run_forever()
				# tasks = asyncio.all_tasks()
				# for t in [t for t in tasks if not (t.done() or t.cancelled())]:
				#     # give canceled tasks the last chance to run
				#     loop.run_until_complete(t)
				
				# print('loop running 3')
			else:
				print('loop not running')
				loop.run_until_complete(self.client.close())

			print(f'Closing HTTPUtil')
		except Exception:
			pass

	async def close(self):
		if self.client:
			await self.client.close()
			self.client = None

	@retry(
		retry=retry_if_exception_type(TryAgain),
		reraise=True,
		wait=wait_exponential(multiplier=1, max=60) + wait_random(0, 3),
		stop=stop_after_attempt(7),
		before_sleep=before_sleep_log(logger, logging.DEBUG)
	)
	async def _call_api(self, method, url, **kwargs):
		assert self.client
		r = await self.client.request(method, url,**kwargs)
		if r.status == 429 or r.status >= 500:
			logger.warning(f'{r.status} returned. Retrying. For {method} {url}')
			raise TryAgain(r.status)
		
		return r

	async def call_api(self, method, url, **kwargs) -> dict:
		if self.client is None:
			timeout = aiohttp.ClientTimeout(connect=60, total=self.timeout)
			self.client = aiohttp.ClientSession(timeout=timeout)
		
		try:
			r = await self._call_api(method, url, **kwargs)

			r.raise_for_status()

			return await r.json()
		
		except TryAgain as e:
			msg = f'Request failed with status code: {e}, for: {method} {url}, {kwargs}'
			raise RuntimeError(msg[:1000])

		except aiohttp.ClientResponseError as e:
			msg = f'Request failed with status code: {e.status} {e.message}, \
						  for url: {method} {e.request_info.url!r}, {kwargs}'
			logger.error(msg[:1000])
			raise
		
		except Exception as e:
			msg = f'Request failed with unknown exception {e}, for: {method} {url}, {kwargs}'
			logger.exception(msg[:1000])
			raise

	async def call_api__text(self, method, url, **kwargs) -> str:
		if self.client is None:
			timeout = aiohttp.ClientTimeout(connect=60, total=300)
			self.client = aiohttp.ClientSession(timeout=timeout)
		
		try:
			r = await self._call_api(method, url, **kwargs)

			r.raise_for_status()

			return await r.text()
		
		except TryAgain as e:
			msg = f'Request failed with status code: {e}, for: {method} {url}, {kwargs}'
			raise RuntimeError(msg[:1000])

		except aiohttp.ClientResponseError as e:
			msg = f'Request failed with status code: {e.status} {e.message}, \
						  for url: {method} {e.request_info.url!r}, {kwargs}'
			logger.error(msg[:1000])
			raise
		
		except Exception as e:
			msg = f'Request failed with unknown exception {e}, for: {method} {url}, {kwargs}'
			logger.exception(msg[:1000])
			raise

	async def call_api_return_bytes(self, method, url, **kwargs) -> bytes:
		if self.client is None:
			timeout = aiohttp.ClientTimeout(connect=30, total=300)
			self.client = aiohttp.ClientSession(timeout=timeout)
		
		try:
			r = await self._call_api(method, url, **kwargs)

			r.raise_for_status()

			return await r.read()
		
		except TryAgain as e:
			msg = f'Request failed with status code: {e}, for: {method} {url}, {kwargs}'
			raise RuntimeError(msg[:1000])

		except aiohttp.ClientResponseError as e:
			msg = f'Request failed with status code: {e.status} {e.message}, \
						  for url: {method} {e.request_info.url!r}, {kwargs}'
			logger.error(msg[:1000])
			raise
		
		except Exception as e:
			msg = f'Request failed with unknown exception {e}, for: {method} {url}, {kwargs}'
			logger.exception(msg[:1000])
			raise


