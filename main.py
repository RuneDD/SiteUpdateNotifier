import requests
import time
import hashlib
from plyer import notification

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

def monitor():
    old_hash = ""
    while True:
        print('Checking for changes...')
        current_content = get_page_content(url)
        current_hash = hashlib.sha224(current_content.encode()).hexdigest()
        if old_hash != "" and old_hash != current_hash:
            print("Change detected, sending notification...")
            send_notification("Webpage Change Detected", "The webpage at {} has changed.".format(url))
        else:
            print('No changes detected.')
        old_hash = current_hash
        print(f'Waiting for {time_between_checks/60} minutes before checking again.')
        time.sleep(time_between_checks)

monitor()
