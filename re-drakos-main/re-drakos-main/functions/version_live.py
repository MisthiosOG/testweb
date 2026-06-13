import aiohttp
import re


async def get_html_content(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.61 Mobile Safari/537.36"
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                return await response.text()
            print(f"Failed to retrieve HTML content. Status code: {response.status}")
            return None


def extract_version_text(html_content):
    match = re.search(r'"vername":"(\d+\.\d+\.\d+ \(\d+\))"', html_content)
    if match:
        version_text = match.group(1)
        return version_text.replace(" ", ".").replace("(", "").replace(")", "")
    return None


async def get_version():
    url = "https://com-tgc-sky-android.en.aptoide.com/app"
    html_content = await get_html_content(url)
    if html_content:
        modified_version_text = extract_version_text(html_content)
        if modified_version_text:
            return modified_version_text
    return None
