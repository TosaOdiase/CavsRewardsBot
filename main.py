import csv
import random
import time
import re
import imaplib
import email
from faker import Faker
from playwright.sync_api import Playwright, sync_playwright

catchall = "gmail.com"


def load_proxies(csv_file):
    proxies = []
    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) == 4:
                proxies.append({
                    "server": f"http://{row[0]}:{row[1]}",
                    "username": row[2],
                    "password": row[3]
                })
    return proxies


def run(playwright: Playwright, proxy: dict) -> None:
    browser = playwright.chromium.launch(headless=False, proxy=proxy)
    context = browser.new_context()
    page = context.new_page()

    page.goto("https://www.cavsrewards.com/")
    time.sleep(1.5)
    page.get_by_placeholder("Referral Code (optional)").click()
    page.get_by_placeholder("Referral Code (optional)").fill("BJjPn")
    time.sleep(5)
    page.get_by_role("button", name="Continue to Cavs Rewards").click()
    time.sleep(5)
    page.get_by_role("link", name="Create account now").click()
    page.get_by_label("Email address").click()
    page.get_by_label("Email address").fill(f"{Faker().last_name()}{random.randint(3305481590, 4405570456)}@{catchall}")
    time.sleep(5)
    page.get_by_label("Password").click()
    page.get_by_label("Password").fill(f"#{Faker().last_name()}{random.randint(3305481590, 4405570456)}$")
    time.sleep(1.5)
    page.get_by_role("button", name="Continue", exact=True).click()
    time.sleep(1.5)
    page.get_by_role("button", name="GET STARTED").click()
    time.sleep(1.5)
    page.get_by_text("By clicking \"Done\", you agree to our Terms of Use Continue").click()
    time.sleep(5)


    # Close context and browser
    context.close()
    browser.close()


def get_activation_link(email_address, email_password):
    imap_server = "imap.gmail.com"
    imap_port = 993
    mail = imaplib.IMAP4_SSL(imap_server, imap_port)
    mail.login(email_address, email_password)
    mail.select("inbox")
    
    while True:
        search_criteria = '(FROM "unitedaccount@cavs.com" SUBJECT "Verify your email for Cavs Rewards")'
        status, email_ids = mail.search(None, search_criteria)
        if email_ids:
            latest_email_id = email_ids[0].split()[-1]
            status, email_data = mail.fetch(latest_email_id, "(RFC822)")
            raw_email = email_data[0][1].decode("utf-8")
            msg = email.message_from_string(raw_email)
            email_content = msg.get_payload()
            url_pattern = r'https://login\.cavs\.com/u/email-verification\?ticket=[^\s#]+#'
            match = re.search(url_pattern, email_content)
            if match:
                full_url = match.group()
                print("Full URL:", full_url)
                return full_url
        time.sleep(60)


def threaded_run():
    proxies = load_proxies("proxies.csv")
    with sync_playwright() as playwright:
        for _ in range(8):  # Number of runs (adjust as needed)
            try:
                proxy = random.choice(proxies)  # Randomly select a proxy
                run(playwright, proxy)
            except Exception as e:
                print(f"An error occurred: {e}")

threaded_run()
