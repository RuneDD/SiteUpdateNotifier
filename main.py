import requests
import time
import hashlib
import logging
import sys
import validators
import re
from plyer import notification
from bs4 import BeautifulSoup

# Constants
TIME_BETWEEN_CHECKS = 60 * 5  # Default value of 5 minutes

# Logging Configuration
logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', level=logging.INFO)

def is_valid_url_using_validators(url):
    return validators.url(url)

def is_valid_url_using_regex(url):
    pattern = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or an IP address
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(pattern, url) is not None

def send_notification(title, message):
    """Sends a desktop notification."""
    notification.notify(title=title, message=message, timeout=10)

def get_page_content(url):
    """Fetches the content of the page at the given URL."""
    if not url.startswith(('http://', 'https://')):
        logging.error(f"Invalid URL: {url}. It must start with 'http://' or 'https://'.")
        return None
    if not is_valid_url_using_validators(url) or not is_valid_url_using_regex(url):
        logging.warning(f"Invalid URL: {url}")
        return None
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses
        return response.content
    except requests.RequestException as e:
        logging.error(f"Failed to fetch content from URL {url}. Error: {e}")
        return None

def filter_content(html_content):
    """Filters the HTML content."""
    soup = BeautifulSoup(html_content, 'html.parser')
    # Custom filtering logic can be added here
    # ...
    return soup.get_text()

def monitor(url):
    """Monitors the webpage for changes."""
    old_hash = ""
    logging.info(f'Waiting for {TIME_BETWEEN_CHECKS/60} minutes before the first check...')
    time.sleep(TIME_BETWEEN_CHECKS)
    while True:
        logging.info('Checking for changes...')
        current_content = get_page_content(url)
        filtered_content = filter_content(current_content)
        current_hash = hashlib.sha224(filtered_content.encode()).hexdigest()
        if old_hash != "" and old_hash != current_hash:
            logging.info("Change detected, sending notification...")
            send_notification("Webpage Change Detected", f"The webpage at {url} has changed.")
        else:
            logging.info('No changes detected.')
        old_hash = current_hash
        logging.info(f'Waiting for {TIME_BETWEEN_CHECKS/60} minutes before checking again.')
        time.sleep(TIME_BETWEEN_CHECKS)

if __name__ == "__main__":
    url_to_monitor = input("Please provide the URL to monitor: ")
    try:
        TIME_BETWEEN_CHECKS = int(input("Please provide the time to wait between checks in seconds: "))
    except ValueError:
        logging.error("Invalid time provided. Using default 5 minutes.")
    monitor(url_to_monitor)
