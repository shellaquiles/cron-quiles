import requests
import re
import sys
from bs4 import BeautifulSoup

def scrape(url):
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    title = soup.find('meta', property='og:title')
    desc = soup.find('meta', property='og:description')
    
    print("URL:", url)
    print("Title:", title['content'] if title else 'No title')
    print("Desc:", desc['content'] if desc else 'No desc')
    
    # Try to find dates
    script = soup.find('script', {'id': '__NEXT_DATA__'})
    if script:
        # Just simple regex
        starts = re.findall(r'"start_at":"([^"]+)"', script.text)
        ends = re.findall(r'"end_at":"([^"]+)"', script.text)
        print("Starts:", starts[0] if starts else 'None')
        print("Ends:", ends[0] if ends else 'None')
        
        timezone = re.findall(r'"timezone":"([^"]+)"', script.text)
        print("Timezone:", timezone[0] if timezone else 'None')
        
        address = re.findall(r'"full_address":"([^"]+)"', script.text)
        print("Address:", address[0] if address else 'None')
        city = re.findall(r'"city":"([^"]+)"', script.text)
        print("City:", city[0] if city else 'None')
    print("-" * 40)

for u in sys.argv[1:]:
    scrape(u)
