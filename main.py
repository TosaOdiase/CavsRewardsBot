import os
import csv
import time
import random
import pandas as pd
from datetime import datetime, timedelta
import subprocess
from faker import Faker
from playwright.sync_api import Playwright, sync_playwright

catchall = "gmail.com"

def load_proxies(csv_file):
    """
    Load proxies from a CSV file.
    """
    if not os.path.exists(csv_file):
        print(f"Error: The file '{csv_file}' does not exist.")
        return []
    
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

def get_proxy_config(proxies):
    """
    Get a random proxy configuration if proxies are provided.
    """
    if proxies:
        proxy = random.choice(proxies)
        return {
            "server": proxy["server"],
            "username": proxy["username"],
            "password": proxy["password"]
        }
    return None

def escape_latex(text):
    """Escape LaTeX special characters."""
    return text.replace("#", "\\#")

def generate_random_receipt():
    """Generate random receipt details."""
    tc_number = escape_latex(f"TC# {random.randint(1000, 9999)} {random.randint(1000, 9999)} {random.randint(1000, 9999)} {random.randint(1000, 9999)}")
    st_number = escape_latex(f"ST# {random.randint(1000, 9999)} OP# {random.randint(1000, 9999)} TE# {random.randint(1, 20)} TR# {random.randint(1000, 9999)}")
    random_date = (datetime.now() - timedelta(days=random.randint(0, 15))).strftime("%m/%d/%y %H:%M:%S")
    amex_number = escape_latex(f"{random.randint(1000, 9999)}")

    # Item names and numbers
    items_dict = {
        "OILSPRAY": "002639599991 F",
        "PLSBY ELF": "001800011925 F",
        "BEEF RIBEYE": "026039400000 F",
        "CHILL 12PK": "004900055539 F",
        "CAKE": "007432309524 F",
        "B J ICECRM": "007684040007 F",
        "GV HF HF": "060538818715 F",
        "GV CK MJ 8Z": "007874203972 F"
    }

    # Fixed MMZ Lemonade
    fixed_item = ("MMZ LEMONADE", "002500012052 F", random.uniform(2.50, 4.50))

    # Randomly select 4 items excluding MMZ Lemonade
    selected_items = random.sample(list(items_dict.items()), 4)

    # Generate random prices for selected items
    items_with_prices = [(name, number, round(random.uniform(10.0, 30.0), 2)) for name, number in selected_items]
    
    # Combine fixed MMZ Lemonade with the random items 
    items = items_with_prices[:2] + [fixed_item] + items_with_prices[2:]

    subtotal = round(sum(price for _, _, price in items), 2)
    tax1 = round(0.07 * subtotal, 2)
    total = round(subtotal + tax1, 2)

    return tc_number, st_number, random_date, amex_number, items, subtotal, tax1, total

def create_receipt_latex(tc_number, st_number, random_date, amex_number, items, subtotal, tax1, total, logo_path, barcode_path):
    """Create LaTeX receipt."""
    items_tabbed = r"""
    \begin{tabbing}
        \hspace{2.5cm} \= \hspace{3.7cm} \= \kill
    """
    for name, number, price in items:
        items_tabbed += f"        \\\textbf{{{name}}} \\> \\\textbf{{{number}}} \\> \\\textbf{{{price:.2f}}}\\\\n"
    items_tabbed += r"    \end{tabbing}"

    receipt_template = r"""
\documentclass{article}
\usepackage{geometry}
\geometry{paperwidth=100mm, paperheight=150mm, left=5mm, top=5mm, right=5mm, bottom=5mm}
\usepackage{courier}
\renewcommand{\familydefault}{\ttdefault}
\usepackage{array}
\usepackage{graphicx}
\usepackage{multicol}
\usepackage{xcolor}
\pagecolor{white}
\usepackage{adjustbox}

\begin{document}
\pagestyle{empty}

\newcommand{\receiptfontsize}{\fontsize{10}{9}\selectfont}
\receiptfontsize

\begin{center}
    \includegraphics[width=\linewidth]{""" + logo_path + r"""} % Walmart logo
    \textbf{WAL*MART}\\
    \textbf{33062990 Mgr. MIRANDA}\\
    \textbf{905 SINGLETARY DR}\\
    \textbf{STREETSBORO, OH}\\
    \textbf{""" + st_number + r"""}\\
    
    \vspace{1mm}
""" + items_tabbed + r"""
    \vspace{-9mm}
    \hspace{2.5cm}\begin{tabbing}
        \hspace{2cm} \= \hspace{2.4cm} \= \kill
        \textbf{\hspace{4cm}SUBTOTAL} \> \textbf{\hspace{4.3cm} """ + str(subtotal) + r"""} \\\\
        \textbf{\hspace{2.5cm}TAX} \hspace{-0.25mm} \textbf{1} \> \textbf{\hspace{2.5cm}7\%} \> \textbf{\hspace{1.90cm} """ + str(tax1) + r"""} \\\\
        \textbf{\hspace{2.5cm}TAX 12} \> \textbf{\hspace{2.5cm}0\%} \> \textbf{\hspace{2.1cm}0.00} \\\\
        \textbf{\hspace{4.75cm}TOTAL} \> \textbf{\hspace{4.3cm} """ + str(total) + r"""} \\\\
        \textbf{\hspace{2.45cm}AMEX CREDIT TEND} \> \textbf{\hspace{4.3cm} """ + str(total) + r"""} \\\\
        \textbf{\hspace{2.7cm}AMEX} \textbf{**** **** **** """ + amex_number + r"""} \\\\
        \textbf{\hspace{3.7cm}CHANGE DUE} \> \textbf{\hspace{4.7cm}0.00} \\\\
    \end{tabbing}
    
    \vspace{-2mm}

    \textbf{\huge{\# ITEMS SOLD 5}}\\
    \vspace{0.5cm}
    \textbf{""" + tc_number + r"""}\\
    \includegraphics[width=\linewidth]{""" + barcode_path + r"""} % Barcode
    \vspace{0.5cm}
    \textbf{""" + random_date + r"""}
\end{center}  
\end{document}
"""
    with open("receipt.tex", "w") as f:
        f.write(receipt_template)

def compile_latex_to_png():
    """Compile LaTeX to PDF and convert to PNG."""
    try:
        subprocess.run(["pdflatex", "receipt.tex"], check=True)
        subprocess.run(["convert", "-density", "200", "receipt.pdf", "-quality", "100", "receipt.png"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error during compilation: {e}")
        return False
    return True

def generate_receipt():
    """Generate and compile receipt to PNG."""
    tc_number, st_number, random_date, amex_number, items, subtotal, tax1, total = generate_random_receipt()
    logo_path = "Header.png"
    barcode_path = "barcode.png"

    # Check if required files exist
    if not os.path.exists(logo_path):
        print(f"Error: '{logo_path}' is missing!")
        return None
    if not os.path.exists(barcode_path):
        print(f"Error: '{barcode_path}' is missing!")
        return None

    create_receipt_latex(tc_number, st_number, random_date, amex_number, items, subtotal, tax1, total, logo_path, barcode_path)
    if compile_latex_to_png():
        for ext in ["aux", "log", "pdf", "tex"]:
            if os.path.exists(f"receipt.{ext}"):
                os.remove(f"receipt.{ext}")
        return "receipt.png"
    return None

def save_account_to_excel(accounts):
    """Save account details to an Excel file."""
    df = pd.DataFrame(accounts)
    if os.path.exists("accounts.xlsx"):
        existing_df = pd.read_excel("accounts.xlsx")
        df = pd.concat([existing_df, df], ignore_index=True)
    df.to_excel("accounts.xlsx", index=False)

def create_account(playwright: Playwright, accounts: list, proxies: list = None) -> None:
    """
    Create an account on Cavs Rewards and store the credentials, optionally using proxies.
    """
    proxy_config = get_proxy_config(proxies)
    browser = playwright.chromium.launch(headless=False, proxy=proxy_config)
    context = browser.new_context()
    page = context.new_page()

    # Navigate to the website and create an account
    page.goto("https://www.cavsrewards.com/")
    time.sleep(1.5)
    page.get_by_placeholder("Referral Code (optional)").click()
    time.sleep(1.5)
    page.get_by_placeholder("Referral Code (optional)").fill("BJjPn")
    time.sleep(1.5)
    page.get_by_role("button", name="Continue to Cavs Rewards").click()
    time.sleep(1.5)
    page.get_by_role("link", name="Create account now").click()
    time.sleep(1.5)
    
    # Generate email and password
    email = f"{Faker().last_name()}{random.randint(3305481590, 4405570456)}@{catchall}"
    password = f"#{Faker().last_name()}{random.randint(3305481590, 4405570456)}$"

    # Fill in the generated email and password
    page.get_by_label("Email address").click()
    time.sleep(1.5)
    page.get_by_label("Email address").fill(email)
    time.sleep(1.5)
    page.get_by_label("Password").click()
    time.sleep(1.5)
    page.get_by_label("Password").fill(password)
    time.sleep(1.5)
    
    # Submit the account creation form
    page.get_by_role("button", name="Continue", exact=True).click()
    time.sleep(1.5)
    page.get_by_role("button", name="GET STARTED").click()
    time.sleep(1.5)
    page.get_by_role("button", name="Continue").click()
    time.sleep(1.5)
    page.get_by_role("button", name="Continue").click()
    time.sleep(1.5)
    page.get_by_role("button", name="Continue").click()
    time.sleep(1.5)
    page.get_by_role("button", name="Continue").click()
    time.sleep(1.5)
    page.locator("svg").click()
    time.sleep(1.5)
    page.get_by_role("button", name="Done").click()
    time.sleep(1.5)

    # Store the email and password in the accounts list
    account_details = {"email": email, "password": password}
    accounts.append(account_details)

    # Save to Excel
    save_account_to_excel(accounts)

    # Close context and browser
    context.close()
    browser.close()

def login_and_upload_receipt(playwright, receipt_path, account, alr_processed, success, proxies: list = None):
    """
    Log into Cavs Rewards and upload a receipt, optionally using proxies.
    """
    proxy_config = get_proxy_config(proxies)
    browser = playwright.chromium.launch(headless=False, proxy=proxy_config)
    context = browser.new_context()
    page = context.new_page()

    # Log into the website
    page.goto('https://www.cavsrewards.com/auth')
    time.sleep(1.5)
    page.get_by_placeholder('Referral Code (optional)').click()
    time.sleep(1.5)
    page.get_by_placeholder('Referral Code (optional)').fill('BJjPn')
    time.sleep(1.5)
    page.get_by_role('button', name="Continue to Cavs Rewards").click()
    time.sleep(1.5)
    page.get_by_label('Email address').fill(account["email"])
    time.sleep(1.5)
    page.get_by_label('Password').fill(account["password"])
    time.sleep(1.5)
    page.get_by_role('button', name="Continue", exact=True).click()
    time.sleep(1.5)
    page.get_by_role('img', name="Close").click()
    time.sleep(1.5)

    # Navigate to the Coca-Cola card
    page.get_by_role('link', name="Card Top Coca-Cola Products").click()
    time.sleep(1.5)

    # Upload the receipt via the actual <input type="file"> element
    page.locator('input[type="file"]').set_input_files(receipt_path)
    time.sleep(1.5)

    # Confirm the upload (if required)
    page.get_by_role('button', name="Check").click()
    time.sleep(20)

    # Check if the specific text exists on the page
    search_text = "This receipt has already been processed. Please upload a different receipt."
    try:
        text_content = page.locator("[id=\"\\31 \"]").text_content(timeout=20000)
        if search_text in text_content:
            alr_processed += 1
    except Exception as e:
        success += 1

    context.close()
    browser.close()
    return alr_processed, success

def main():
    """
    Main function to run the process in a loop.
    """
    alr_processed = 0
    success = 0
    accounts = []
    proxies = load_proxies("proxies.csv")  # Load proxies from a CSV file

    with sync_playwright() as playwright:
        while True:
            if len(accounts) == 0 or len(accounts) < 5:
                create_account(playwright, accounts, proxies)

            receipt_path = generate_receipt()
            if not receipt_path:
                print("Failed to generate receipt. Exiting...")
                break

            for account in accounts:
                alr_processed, success = login_and_upload_receipt(playwright, receipt_path, account, alr_processed, success, proxies)
                print(f"Errored receipts: {alr_processed}")
                print(f"Successful uploads: {success}")

            time.sleep(1.5)

if __name__ == "__main__":
    main()

