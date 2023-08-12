import requests
import time
import hashlib
from plyer import notification
from bs4 import BeautifulSoup

# URL to be scraped
url = ""

# Time between checks in seconds
time_between_checks = 60 * 5  # Five minutes

def send_notification(title, message):
    notification.notify(
        title=title,
        message=message,
        timeout=10
    )

def get_page_content(url):
    print(f'Fetching content from {url}')
    response = requests.get(url)
    return response.text

def filter_content(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove script and style elements
    for script in soup(["script", "style", "meta"]):
        script.extract()
    
    # Get text
    text = soup.get_text()
    
    # Break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    
    # Break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    
    # Drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)
    
    return text

def monitor():
    old_hash = ""
    print(f'Waiting for {time_between_checks/60} minutes before the first check...')
    time.sleep(time_between_checks)  # Wait for 5 minutes before the first check
    while True:
        print('Checking for changes...')
        current_content = get_page_content(url)
        filtered_content = filter_content(current_content)
        current_hash = hashlib.sha224(filtered_content.encode()).hexdigest()
        if old_hash != "" and old_hash != current_hash:
            print("Change detected, sending notification...")
            send_notification("Webpage Change Detected", "The webpage at {} has changed.".format(url))
        else:
            print('No changes detected.')
        old_hash = current_hash
        print(f'Waiting for {time_between_checks/60} minutes before checking again.')
        time.sleep(time_between_checks)

monitor()
