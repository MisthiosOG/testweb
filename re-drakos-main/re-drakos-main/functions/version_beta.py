import aiohttp
from bs4 import BeautifulSoup
import re


async def get_html_content(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.61 Mobile Safari/537.36"
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                return await response.text()
            print(f"Failed to retrieve HTML content from {url}. Status code: {response.status}")
            return None


def extract_version_text(soup):
    details_sdk_tag = soup.find('p', class_='details_sdk')
    if details_sdk_tag:
        version_element = details_sdk_tag.find('span')
        if version_element:
            version_text = version_element.text.strip()
            version_text_match = re.search(r'(\d+\.\d+\.\d+ \(\d+\))', version_text)
            if version_text_match:
                extracted_text = version_text_match.group(1)
                return extracted_text.replace(' ', '.').replace('(', '').replace(')', '')
    return None


async def get_version():
    url = "https://apkpure.com/beta-sky-children-of-the-li/com.tgc.sky.android.test.gold"
    html_content = await get_html_content(url)
    if html_content:
        soup = BeautifulSoup(html_content, 'html.parser')
        modified_version_text = extract_version_text(soup)
        return modified_version_text if modified_version_text else None
    return None
