from datetime import datetime, date, timedelta
import requests
import json
import aiohttp


async def get_user_ip(request):
    x_forwarded_for = await request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = await request.META.get('REMOTE_ADDR')
    return ip


async def datetime_now():
    now = datetime.now()
    return now


async def time_now():
    now = datetime.now()
    return now.time()


async def today():
    today = date.today()
    return today


async def send_request(url, data=None, headers=None, type='get') -> dict:
    if type == 'get':
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=data) as response:
                response: aiohttp.ClientResponse
                if 'application/json' in response.headers.get('Content-Type', ''):
                    return await response.json()
                else:
                    response_text = await response.text()
                    return json.loads(response_text)
    else:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                response: aiohttp.ClientResponse
                if 'application/json' in response.headers.get('Content-Type', ''):
                    return await response.json()
                else:
                    response_text = await response.text()
                    return json.loads(response_text)


class DictToClass:
    def __init__(self, dictionary=None):
        if dictionary is not None:
            for key, value in dictionary.items():
                if isinstance(value, dict):
                    # If the value is a dictionary, recursively create an instance of the class
                    setattr(self, key, DictToClass(value))
                elif isinstance(value, list):
                    # If the value is a list, process each item in the list
                    setattr(self, key, [DictToClass(item) if isinstance(
                        item, dict) else item for item in value])
                else:
                    # Otherwise, set the attribute to the value
                    setattr(self, key, value)

    def __setattr__(self, key, value):
        if isinstance(value, dict):
            # If the value is a dictionary, convert it to an instance of DictToClass
            super().__setattr__(key, DictToClass(value))
        elif isinstance(value, list):
            # If the value is a list, convert any dictionaries in the list to DictToClass
            super().__setattr__(key, [DictToClass(item) if isinstance(
                item, dict) else item for item in value])
        else:
            # Otherwise, just set the attribute
            super().__setattr__(key, value)

    def __getattr__(self, key):
        # If the attribute doesn't exist, automatically create a DictToClass instance
        # This allows you to add nested attributes dynamically
        self.__setattr__(key, DictToClass())
        return self.__dict__[key]

    @property
    async def to_dict(self):
        # This method converts the class instance back into a dictionary
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, DictToClass):
                # If the value is another instance of DictToClass, recursively call to_dict
                result[key] = await value.to_dict
            elif isinstance(value, list):
                # If the value is a list, ensure each element is converted back to a dictionary if necessary
                result[key] = [
                    await item.to_dict if isinstance(item, DictToClass) else item for item in value
                ]
            else:
                # Otherwise, just add the key-value pair to the result dictionary
                result[key] = value
        return result

    def __repr__(self):
        # This will allow a readable representation of the object when printed
        return f"{self.__class__.__name__}({self.__dict__})"
