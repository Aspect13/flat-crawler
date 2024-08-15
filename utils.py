import re
from typing import Optional

from models import Flat
import aiohttp

parser_regexp = {
    'district':  re.compile(r".*#([^\s]*)"),
    'address': re.compile(r"\n(.*)\n\n"),
    'rooms': re.compile(r"Комнат.*(\d+)"),
    'area': re.compile(r"Площадь.* (\d+)"),
    'floors': re.compile(r"Этаж.* ((\d+)/?(\d*))"),
    'price': re.compile(r"Цена.* (\d+)\$"),
    'location': re.compile(r"Локация.*\((.*)\)"),
    'description': re.compile(r"__(.*)__", flags=re.MULTILINE | re.DOTALL)
}


def parse_message(message_text: str, flat_object: Optional[Flat] = None) -> Flat:
    if flat_object is None:
        flat_object = Flat()
    flat_object.rooms = parser_regexp['rooms'].search(message_text).group(1)
    flat_object.area = parser_regexp['area'].search(message_text).group(1)
    floors = parser_regexp['floors'].search(message_text)
    flat_object.floor = floors.group(2)
    flat_object.floors = floors.group(3)
    flat_object.price = parser_regexp['price'].search(message_text).group(1)
    try:
        flat_object.location = parser_regexp['location'].search(message_text).group(1)
    except AttributeError:
        flat_object.location = ''    
    try:
        flat_object.description = parser_regexp['description'].search(message_text).group(1)
    except AttributeError:
        flat_object.description = ''
    flat_object.address = parser_regexp['address'].search(message_text).group(1)

    if not flat_object.district:
        flat_object.district = parser_regexp['district'].search(message_text).group(1).lower()
    return flat_object
