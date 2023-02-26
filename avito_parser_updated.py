import sqlite3
import time as tm

import requests
import ssl
from datetime import *


# avito security pass
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
from requests.packages.urllib3.util import ssl_

CIPHERS = """ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-SHA384:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-SHA256:AES256-SHA"""
URL_LINK = "https://www.avito.ru"

TOKEN = 'INSERT TOKEN' #Вставить токен
chat_id = '-890118507'
# -890118507

class TlsAdapter(HTTPAdapter):
    def __init__(self, ssl_options=0, **kwargs):
        self.ssl_options = ssl_options
        super(TlsAdapter, self).__init__(**kwargs)

    def init_poolmanager(self, *pool_args, **pool_kwargs):
        ctx = ssl_.create_urllib3_context(ciphers=CIPHERS, cert_reqs=ssl.CERT_REQUIRED, options=self.ssl_options)
        self.poolmanager = PoolManager(*pool_args, ssl_context=ctx, **pool_kwargs)

def get_offer(item):
    item_time = datetime.strftime(datetime.fromtimestamp(item["time"]), '%d.%m.%Y в %H:%M')
    offer = {
        'name': item["title"],
        'price': item["price"].replace(' ₽', ''),
        'time': item_time,
        'place': item["location"],
        'link': URL_LINK + item["uri_mweb"],
        'item_id': item["id"]
    }
    return offer


def format_text(offer):
    text = f"""
Название: {offer["name"]}
Цена: {offer["price"]} руб.
Время публикации: {offer["time"]}
Местоположение: {offer["place"]}
Ссылка: {offer["link"]}
    """
    return text


def send_telegram(offer):
    url_bot = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    text = format_text(offer)
    data = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'}
    response = requests.post(url=url_bot, data=data)


def check_database(item):
    offer_id = item["id"]
    with sqlite3.connect('avito.db') as connection:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT offer_id FROM offers_avito WHERE offer_id = (?)
            """, (offer_id,))
        result = cursor.fetchone()
        if result is None:
            offer = get_offer(item)
            send_telegram (offer)
            cursor.execute("""
                INSERT INTO offers_avito VALUES
                    (NULL, :name, :price, :time, :place, :link, :item_id)
                """, offer)
            connection.commit()
            print(f'Объявление {offer_id} добавлено в БД')

def get_offers(data):
    items = data["result"]["items"]
    for item in items:
        check_database(item["value"])
        break


def get_json():
    cookies = {
        'u': '2tl35p42.uimfli.16836kdb5mh00',
        'buyer_laas_location': '637640',
        '_gcl_au': '1.1.727124238.1669806221',
        'tmr_lvid': '0e7409f13200987bf1069ae52771a181',
        'tmr_lvidTS': '1669806220693',
        '_ga': 'GA1.1.1411445251.1669806221',
        '_ym_uid': '1669806221173875182',
        '_ym_d': '1669806221',
        '__zzatw-avito': 'MDA0dBA=Fz2+aQ==',
        'cfidsw-avito': 'Y2vg4aGY2r2afUvTXw0OCyNdGHWkz4SEBjKULPkZ0hykmLwGuxG7Xsfv7xQCgb5FJ4XQzdQrjBh6URVgGH5q77gXzfaReCwZ2t/KEL4ZNLtENs4J0ZoQxG+h/N259R7YhM7SyWB45pJJN6KT8RpE0GB0bP6/Rs6HjB2L',
        'gsscw-avito': 'xTLZWr5bhBvPhK0HqooklhGG87NDdiktoMZqFVECtOyOAShWWuFVIoFXjlrFAsj2Fp9JliD/5bEdPuTiCwtP7RZfPWIXrW/DYUpXyJagzZ/KbR97rK5d2newSbjFgJ3jwVxj9IOvB9B42q7bGnApwBoWsa+1wIRaX5xjEKI3v3f6vcfrIV/GsRenhz9DzSdN33sfUNLkzihqAdxg3wByqzCzPiEVmGegIY2iRrGmt6VmZqG8r19n5KiLoL/TYg==',
        'sessid': '6e32b0d46b9cea676d51e50da2475d53.1669806226',
        'fgsscw-avito': 'VzIr004aa5fd7b83c10c144fea7e3defd3ac6113',
        'uxs_uid': 'a9e16ca0-709e-11ed-9569-4d428e354b9a',
        '_ym_isad': '1',
        'f': '5.cc913c231fb04ceddc134d8a1938bf88a68643d4d8df96e9a68643d4d8df96e9a68643d4d8df96e9a68643d4d8df96e94f9572e6986d0c624f9572e6986d0c624f9572e6986d0c62ba029cd346349f36c1e8912fd5a48d02c1e8912fd5a48d0246b8ae4e81acb9fa143114829cf33ca746b8ae4e81acb9fa46b8ae4e81acb9fae992ad2cc54b8aa8af305aadb1df8ceb7994eef3d20b6b79f64e692af6fe3777915ac1de0d034112ad09145d3e31a56946b8ae4e81acb9fae2415097439d4047d50b96489ab264edc772035eab81f5e1e992ad2cc54b8aa8d99271d186dc1cd03de19da9ed218fe23de19da9ed218fe23de19da9ed218fe2e992ad2cc54b8aa846b8ae4e81acb9fa38e6a683f47425a8352c31daf983fa077a7b6c33f74d335c76ff288cd99dba4666be20ce2cab3354cd0833ebb6c2bf42e9093fd371b023d5a5cb2cb4473bfe110e28148569569b79995b393b82b3ba45b70a717081f83b722ebf3cb6fd35a0ac0df103df0c26013a28a353c4323c7a3a140a384acbddd748b487f2fb8a004b6b3de19da9ed218fe23de19da9ed218fe2ddb881eef125a8703b2a42e40573ac3c9ca703028dd55cfb3882be5d35524c6c',
        'ft': '"W8COu7l1zL08ruYpz7MItPDEfH2Edy11yI+OJRv+T2X62dNaFFOXnjMc2X/L6iSFSSAHaM+By8W/biV94TLoUiSbaghHGBMChRba9M2enWp8K4yveAfbla+QoKo/J0+cbO4DNvN0/LKPLyI3JJ+U7zWQfUScHQ542NhuBZjvl+tfRgTAXw5djYCe+LzpGU0I"',
        '_ym_visorc': 'b',
        'buyer_location_id': '637640',
        'luri': 'moskva',
        'isLegalPerson': '0',
        'v': '1669927799',
        'dfp_group': '2',
        'sx': 'H4sIAAAAAAAC%2F5yWz5bjKg%2FE36XXsxAgQMzbgPiThHRwgm0c3zPv%2Fh3f73RmMrvb2yx%2BLkqlUv75kEY2m%2Fp9uTyp184daido%2FePnPx%2Frx8%2BPT30aXeXzKIVbbTgG4WBABGRo7ePHR%2Fr4KYwFEEII%2BPXjQ5rezmULbh6ljdKJBpVKZXwhbdY66SAzWuUia%2BmsCCwtKcXSW0gegYj8G1tqdbCnq8hVrenqacDo1JgqlsJf7NL3FgUvrCo0htY7VGqt1VJqr%2BMNaYQ9kPMuy%2FlW9T5KqVwL02gdgb6QkGyQMUTLQTtpCV1CDlZax96gEB7i8ZP%2Bky3RmF8%2FPlR0bIOURqiM0uskszECJAtNxhF8fYLiZdnmhXBGMd%2FmLjbuS1TR%2BV7irN6NMHSQR1zvAemUxkCkMiqVUmmUl8mlyg0mO8tP0zbbxYZPfZ9MqbcJTvgnEsgdSOwVbj5L9rU0br13PKLA5Vsq6Xi%2FTsJAcMhBJGWMl5k1oELWHmQSr6n1k%2Fksm7zvo4C6eV5ylrXOfQvFoXtzFhweIdMnlnD7rDfLo%2FZK0EovA8YrZAGlhmh8AIUkvJYpQhJSsAnSM8vEYIVlfFcN8mBf4OGpqaerA3oZFfnIRftCX7ZrX6zS8OjlsuxjlU%2B%2B7jD5Le8Zzu9qzZExY4zhaE12xmmDxiUbknLRamC20b0c3tW6xGefP6c6Y33sqtzMYoOeOEaf%2FiTj%2F7WaqeOq1LPkPhCIB%2FY%2BSqvjG2IFIB7Ix1gfpHg910bjeD80ot7a96alD%2BS2DwcXXhUCD%2BitAjOM%2BjutloSMQmrvCI3J2duYMrjstEJWAaw2DsG%2B7ZhShwPW5YTzM69XqAWpVqZSqLT6xU4uOAKMCbz1yqFxPjIQOtakvDKWLHh28k%2B2kvZImY06M6RE2QqdbVaWOCljUUhngnjNbYTpelmsU3Lp8Xmrdhui3Je4LmeD%2B%2F2vInMHeaXzuJ2YZiqDK3caWFsfr5UQk1%2F2le%2BlaR6lNehcax1UqCE1ehMr6AgZpXC6js%2FbrQ%2BovXTi3lob%2FJrbqfo8hYtoalsd2PPVTg%2BWJES4XrK8v89NHPtL0wRPUc2mEUfhwZXq4PG7ZaCCdJ86PHtdllo3cUnT5MuyzLec1fx%2BHfRhqTuXXe73Xa3ERFgHw%2BgN6RXY0%2B083Z6RFgIAYqyIo7bOY3QC6G8PV3AE1ieLWUWLkpST3oVgnTWUhZEuByO%2FyHd1y9Nj3US4nder7HOZZCmmnsS2cXR%2FbddhafAbzE%2Ftm62EbZSBR9ESvMTe2X7STqsm9nrp8kGfJT%2FTvJz384X%2FOgn6sDTkwEKAVEqrnIURzsqkOSJJso7zt0pGH2JZ4GW%2BXdKqBiM37sS10h%2FD%2BtaSSSMOtgYZovGKPQNQQHBSBRtS9ArI2K9PVPeptJRKuWd6qj12XBfxYOStjlPz76rVcdE5iJwFoUGdorHGaE8pOelsjhJ%2Fn4j%2FlLR%2FTwRnRUYHi9pk7TChA2G0Vzo5k1Q0L6cfq%2Bg0r9q3x%2FU08fXxyWXnNl39ePS%2FSlccdZacDUIJAxxjpAgxKps9CtQkQwb1RW76zr3fy8SUl9OjJ20uY%2BcESnbct7%2FcONKRRRy36mbV2%2BBB1DsWbKV9z4Z%2FmyaLc%2FL57ufUSmXmVmm0Ufn158MTJlLJkJIktDaCslQarEVWKqrovfLKh%2FwuV8pfv%2F4XAAD%2F%2F5Kt0bw%2BCgAA',
        'redirectMav': '1',
        '_mlocation': '621540',
        '_mlocation_mode': 'default',
        '_ga_M29JC28873': 'GS1.1.1669917754.11.1.1669927862.1.0.0',
        'tmr_detect': '1%7C1669927862561',
        'isCriteoSetNew': 'true',
    }

    headers = {
        'authority': 'm.avito.ru',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en,ru-RU;q=0.9,ru;q=0.8',
        'cache-control': 'no-cache',
        'content-type': 'application/json;charset=utf-8',
        # Requests sorts cookies= alphabetically
        # 'cookie': 'u=2tl35p42.uimfli.16836kdb5mh00; buyer_laas_location=637640; _gcl_au=1.1.727124238.1669806221; tmr_lvid=0e7409f13200987bf1069ae52771a181; tmr_lvidTS=1669806220693; _ga=GA1.1.1411445251.1669806221; _ym_uid=1669806221173875182; _ym_d=1669806221; __zzatw-avito=MDA0dBA=Fz2+aQ==; cfidsw-avito=Y2vg4aGY2r2afUvTXw0OCyNdGHWkz4SEBjKULPkZ0hykmLwGuxG7Xsfv7xQCgb5FJ4XQzdQrjBh6URVgGH5q77gXzfaReCwZ2t/KEL4ZNLtENs4J0ZoQxG+h/N259R7YhM7SyWB45pJJN6KT8RpE0GB0bP6/Rs6HjB2L; gsscw-avito=xTLZWr5bhBvPhK0HqooklhGG87NDdiktoMZqFVECtOyOAShWWuFVIoFXjlrFAsj2Fp9JliD/5bEdPuTiCwtP7RZfPWIXrW/DYUpXyJagzZ/KbR97rK5d2newSbjFgJ3jwVxj9IOvB9B42q7bGnApwBoWsa+1wIRaX5xjEKI3v3f6vcfrIV/GsRenhz9DzSdN33sfUNLkzihqAdxg3wByqzCzPiEVmGegIY2iRrGmt6VmZqG8r19n5KiLoL/TYg==; sessid=6e32b0d46b9cea676d51e50da2475d53.1669806226; fgsscw-avito=VzIr004aa5fd7b83c10c144fea7e3defd3ac6113; uxs_uid=a9e16ca0-709e-11ed-9569-4d428e354b9a; _ym_isad=1; f=5.cc913c231fb04ceddc134d8a1938bf88a68643d4d8df96e9a68643d4d8df96e9a68643d4d8df96e9a68643d4d8df96e94f9572e6986d0c624f9572e6986d0c624f9572e6986d0c62ba029cd346349f36c1e8912fd5a48d02c1e8912fd5a48d0246b8ae4e81acb9fa143114829cf33ca746b8ae4e81acb9fa46b8ae4e81acb9fae992ad2cc54b8aa8af305aadb1df8ceb7994eef3d20b6b79f64e692af6fe3777915ac1de0d034112ad09145d3e31a56946b8ae4e81acb9fae2415097439d4047d50b96489ab264edc772035eab81f5e1e992ad2cc54b8aa8d99271d186dc1cd03de19da9ed218fe23de19da9ed218fe23de19da9ed218fe2e992ad2cc54b8aa846b8ae4e81acb9fa38e6a683f47425a8352c31daf983fa077a7b6c33f74d335c76ff288cd99dba4666be20ce2cab3354cd0833ebb6c2bf42e9093fd371b023d5a5cb2cb4473bfe110e28148569569b79995b393b82b3ba45b70a717081f83b722ebf3cb6fd35a0ac0df103df0c26013a28a353c4323c7a3a140a384acbddd748b487f2fb8a004b6b3de19da9ed218fe23de19da9ed218fe2ddb881eef125a8703b2a42e40573ac3c9ca703028dd55cfb3882be5d35524c6c; ft="W8COu7l1zL08ruYpz7MItPDEfH2Edy11yI+OJRv+T2X62dNaFFOXnjMc2X/L6iSFSSAHaM+By8W/biV94TLoUiSbaghHGBMChRba9M2enWp8K4yveAfbla+QoKo/J0+cbO4DNvN0/LKPLyI3JJ+U7zWQfUScHQ542NhuBZjvl+tfRgTAXw5djYCe+LzpGU0I"; _ym_visorc=b; buyer_location_id=637640; luri=moskva; isLegalPerson=0; v=1669927799; dfp_group=2; sx=H4sIAAAAAAAC%2F5yWz5bjKg%2FE36XXsxAgQMzbgPiThHRwgm0c3zPv%2Fh3f73RmMrvb2yx%2BLkqlUv75kEY2m%2Fp9uTyp184daido%2FePnPx%2Frx8%2BPT30aXeXzKIVbbTgG4WBABGRo7ePHR%2Fr4KYwFEEII%2BPXjQ5rezmULbh6ljdKJBpVKZXwhbdY66SAzWuUia%2BmsCCwtKcXSW0gegYj8G1tqdbCnq8hVrenqacDo1JgqlsJf7NL3FgUvrCo0htY7VGqt1VJqr%2BMNaYQ9kPMuy%2FlW9T5KqVwL02gdgb6QkGyQMUTLQTtpCV1CDlZax96gEB7i8ZP%2Bky3RmF8%2FPlR0bIOURqiM0uskszECJAtNxhF8fYLiZdnmhXBGMd%2FmLjbuS1TR%2BV7irN6NMHSQR1zvAemUxkCkMiqVUmmUl8mlyg0mO8tP0zbbxYZPfZ9MqbcJTvgnEsgdSOwVbj5L9rU0br13PKLA5Vsq6Xi%2FTsJAcMhBJGWMl5k1oELWHmQSr6n1k%2Fksm7zvo4C6eV5ylrXOfQvFoXtzFhweIdMnlnD7rDfLo%2FZK0EovA8YrZAGlhmh8AIUkvJYpQhJSsAnSM8vEYIVlfFcN8mBf4OGpqaerA3oZFfnIRftCX7ZrX6zS8OjlsuxjlU%2B%2B7jD5Le8Zzu9qzZExY4zhaE12xmmDxiUbknLRamC20b0c3tW6xGefP6c6Y33sqtzMYoOeOEaf%2FiTj%2F7WaqeOq1LPkPhCIB%2FY%2BSqvjG2IFIB7Ix1gfpHg910bjeD80ot7a96alD%2BS2DwcXXhUCD%2BitAjOM%2BjutloSMQmrvCI3J2duYMrjstEJWAaw2DsG%2B7ZhShwPW5YTzM69XqAWpVqZSqLT6xU4uOAKMCbz1yqFxPjIQOtakvDKWLHh28k%2B2kvZImY06M6RE2QqdbVaWOCljUUhngnjNbYTpelmsU3Lp8Xmrdhui3Je4LmeD%2B%2F2vInMHeaXzuJ2YZiqDK3caWFsfr5UQk1%2F2le%2BlaR6lNehcax1UqCE1ehMr6AgZpXC6js%2FbrQ%2BovXTi3lob%2FJrbqfo8hYtoalsd2PPVTg%2BWJES4XrK8v89NHPtL0wRPUc2mEUfhwZXq4PG7ZaCCdJ86PHtdllo3cUnT5MuyzLec1fx%2BHfRhqTuXXe73Xa3ERFgHw%2BgN6RXY0%2B083Z6RFgIAYqyIo7bOY3QC6G8PV3AE1ieLWUWLkpST3oVgnTWUhZEuByO%2FyHd1y9Nj3US4nder7HOZZCmmnsS2cXR%2FbddhafAbzE%2Ftm62EbZSBR9ESvMTe2X7STqsm9nrp8kGfJT%2FTvJz384X%2FOgn6sDTkwEKAVEqrnIURzsqkOSJJso7zt0pGH2JZ4GW%2BXdKqBiM37sS10h%2FD%2BtaSSSMOtgYZovGKPQNQQHBSBRtS9ArI2K9PVPeptJRKuWd6qj12XBfxYOStjlPz76rVcdE5iJwFoUGdorHGaE8pOelsjhJ%2Fn4j%2FlLR%2FTwRnRUYHi9pk7TChA2G0Vzo5k1Q0L6cfq%2Bg0r9q3x%2FU08fXxyWXnNl39ePS%2FSlccdZacDUIJAxxjpAgxKps9CtQkQwb1RW76zr3fy8SUl9OjJ20uY%2BcESnbct7%2FcONKRRRy36mbV2%2BBB1DsWbKV9z4Z%2FmyaLc%2FL57ufUSmXmVmm0Ufn158MTJlLJkJIktDaCslQarEVWKqrovfLKh%2FwuV8pfv%2F4XAAD%2F%2F5Kt0bw%2BCgAA; redirectMav=1; _mlocation=621540; _mlocation_mode=default; _ga_M29JC28873=GS1.1.1669917754.11.1.1669927862.1.0.0; tmr_detect=1%7C1669927862561; isCriteoSetNew=true',
        'pragma': 'no-cache',
        'referer': 'https://m.avito.ru/items/search?locationId=637640&localPriority=0&geoCoords=55.755814%2C37.617635&sort=date&query=uniqlo%20u&presentationType=serp',
        'sec-ch-ua': '"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36',
        'x-laas-timezone': 'Europe/Moscow',
    }

    URL = 'https://m.avito.ru/api/11/items?key=af0deccbgcgidddjgnvljitntccdduijhdinfgjgfjir&locationId=637640&localPriority=0&geoCoords=55.755814,37.617635&sort=date&query=uniqlo+u&page=1&lastStamp=1669927860&display=list&limit=25&presentationType=serp'

    session = requests.session()
    adapter = TlsAdapter(ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1)
    session.mount("https://", adapter)

    response = session.request('GET', url=URL, cookies=cookies, headers=headers)
    data = response.json()
    return data


def main():
    data = get_json()
    get_offers(data)


if __name__ == '__main__':
    while True:
        main()
        tm.sleep(30)
