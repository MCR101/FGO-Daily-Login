# Thanks to atlas academy for this script!
# All credits to atlas
# Github: github.com/atlasacademy
# Website: atlasacademy.io
# Api: api.atlasacademy.io
# Apps: apps.atlasacademy.io

import re
import time

import json5
import httpx
import lxml.html

PLAY_STORE_URL = {
    "NA": "https://play.google.com/store/apps/details?id=com.aniplex.fategrandorder.en",
    "JP": "https://play.google.com/store/apps/details?id=com.aniplex.fategrandorder",
    "KR": "https://play.google.com/store/apps/details?id=com.netmarble.fgok",
    "TW": "https://play.google.com/store/apps/details?id=com.xiaomeng.fategrandorder",
}

PLAY_STORE_XPATH_1 = "/html/body/div[1]/div[4]/c-wiz/div/div[2]/div/div/main/c-wiz[4]/div[1]/div[2]/div/div[4]/span/div/span"
PLAY_STORE_XPATH_2 = "/html/body/div[1]/div[4]/c-wiz/div/div[2]/div/div/main/c-wiz[3]/div[1]/div[2]/div/div[4]/span/div/span"
PLAY_STORE_XPATH_3 = '//div[div[text()="Current Version"]]/span/div/span/text()'
VERSION_REGEX = re.compile(r"^\d+\.\d+\.\d+$")

def get_play_store_ver(region: str):

    play_store_response = httpx.get(PLAY_STORE_URL[region], follow_redirects=True)
    play_store_html = lxml.html.fromstring(play_store_response.text)

    for xpath in (PLAY_STORE_XPATH_1, PLAY_STORE_XPATH_2, PLAY_STORE_XPATH_3):
        try:
            xpath_version: str = play_store_html.xpath(xpath)[0].text
            if VERSION_REGEX.match(xpath_version):
                return xpath_version
        except:  # pylint: disable=bare-except
            continue

    for match in re.finditer(
        r"<script nonce=\"\S+\">AF_initDataCallback\((.*?)\);",
        play_store_response.text,
    ):
        try:
            data = json5.loads(match.group(1))
            if (
                "data" in data
                and len(data["data"]) > 2
                and isinstance(data["data"][1], str)
                and VERSION_REGEX.match(data["data"][1])
            ):
                return data["data"][1]

            deep_version = data["data"][1][2][140][0][0][0]
            if isinstance(deep_version, str) and VERSION_REGEX.match(deep_version):
                return deep_version

        except:  # pylint: disable=bare-except
            pass

    return None

def get_version(region: str) -> None:
    play_store_version = get_play_store_ver(region)
    if play_store_version is not None:
        return play_store_version
    else:
        return "ver.2.70.0"
