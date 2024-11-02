from playwright.sync_api import Playwright, sync_playwright
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from faker import Faker
import random

catchall = "snkrsgate.com"
def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://www.cavsrewards.com/")
    page.goto("https://www.cavsrewards.com/auth")
    time.sleep(1.5)
    page.get_by_placeholder("Referral Code (optional)").click()
    page.get_by_placeholder("Referral Code (optional)").fill("8aQtz")
    time.sleep(1.5)
    page.get_by_role("button", name="Continue to Cavs Rewards").click()
    time.sleep(1.5)
    page.get_by_role("link", name="Create account now").click()
    page.get_by_label("Email address").click()
    page.get_by_label("Email address").fill(f"{Faker().last_name()}{random.randint(3305481590, 4405570456)}@{catchall}")
    time.sleep(1.5)
    page.get_by_label("Password").click()
    page.get_by_label("Password").fill("L$ilvee105$")
    time.sleep(1.5)
    page.get_by_role("button", name="Continue", exact=True).click()
    page.get_by_role("button", name="GET STARTED").click()
    page.get_by_text("By clicking \"Done\", you agree to our Terms of Use Continue").click()
    time.sleep(1.5)
    # ---------------------
    context.close()
    browser.close()


def threaded_run():
    with sync_playwright() as playwright:
        for _ in range(25):  # Run each thread 180 times
            try:
                run(playwright)
            except Exception as e:
                print(f"An error occurred: {e}")

threaded_run()
