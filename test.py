import re
import requests
import html

url = 'https://www.youtube.com/@Appleguy/about'

# Send an HTTP GET request to the URL
response = requests.get(url, cookies={'CONSENT': 'YES+42'})

# Get the content of the response
text = response.text

# Use the regular expression to match the content for the meta tag with the itemprop="description" attribute
pattern = r'itemprop="description"\s+content="([^"]+)"'

match = re.search(pattern, text)
if match:
    content = match.group(1)
    html_unescaped = html.unescape(content)
    print(html_unescaped)
else:
    print("No match found.")