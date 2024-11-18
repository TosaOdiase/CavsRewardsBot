import random
from datetime import datetime, timedelta
import os
import subprocess

def escape_latex(text):
    return text.replace("#", "\#")

def generate_random_receipt():
    # Generate random TC number
    tc_number = escape_latex(f"TC# {random.randint(1000, 9999)} {random.randint(1000, 9999)} {random.randint(1000, 9999)} {random.randint(1000, 9999)} {random.randint(1000, 9999)}")

    # Generate random ST number
    st_number = escape_latex(f"ST# {random.randint(1000, 9999)} OP# {random.randint(1000, 9999)} TE# {random.randint(1, 20)} TR# {random.randint(1000, 9999)}")

    # Generate random date within the last 15 days
    random_date = (datetime.now() - timedelta(days=random.randint(0, 15))).strftime("%m/%d/%y %H:%M:%S")

    # Generate random AMEX last 4 digits
    amex_number = escape_latex(f"AMEX **** **** **** {random.randint(1000, 9999)}")

    return tc_number, st_number, random_date, amex_number



def create_receipt_latex(tc_number, st_number, random_date, amex_number):
    receipt_template = r"""
\documentclass{article}
\usepackage{geometry}
\geometry{paperwidth=80mm, paperheight=200mm, left=5mm, top=5mm, right=5mm, bottom=5mm}
\usepackage{courier}
\renewcommand{\familydefault}{\ttdefault}
\usepackage{array}
\usepackage{graphicx}
\usepackage{multicol}
\usepackage{xcolor}
\pagecolor{white} % Ensure white background

\begin{document}
\pagestyle{empty}

\begin{center}
    \includegraphics[width=\linewidth]{Header.png}
    \textbf{WAL*MART}\\
    TBD Mgr. TBD\\
    905 SINGLETARY DR\\
    STREETSBORO, OH\\
    """ + st_number + r"""\\
    \vspace{10pt}

    \begin{tabbing}
        \hspace{2cm} \= \hspace{3cm} \= \kill
        FANTA \> 004900003073 F \> 6.68
    \end{tabbing}

    \begin{tabbing}
        \hspace{5cm} \= \kill
        SUBTOTAL \> 6.68\\
        TAX 1 \hspace{.5cm} 7\% \> 0.47\\
        TOTAL \> 6.68\\
        AMEX CREDIT TEND \> 7.15\\
    """ + amex_number + r"""\\
        CHANGE DUE \hspace{0.5cm} \> 0.00\\
    \end{tabbing}

    \vspace{10pt}
    {\LARGE \textbf{\# ITEMS SOLD 1}}\\
    \vspace{10pt}

    """ + tc_number + r"""\\
    \vspace{5pt}

    % Include the barcode image
    \includegraphics[width=\linewidth]{barcode.png}

    \vspace{5pt}

    """ + random_date + r"""\\
    \vspace{10pt}
\end{center}

\end{document}
"""
    with open("receipt.tex", "w") as f:
        f.write(receipt_template)


def compile_latex_to_png():
    # Compile LaTeX to PDF
    subprocess.run(["pdflatex", "receipt.tex"], check=True)

    # Convert PDF to PNG
    subprocess.run(["convert", "-density", "300", "receipt.pdf", "-quality", "90", "receipt.png"], check=True)


def main():
    # Generate random details for the receipt
    tc_number, st_number, random_date, amex_number = generate_random_receipt()

    # Create the LaTeX receipt with the generated details
    create_receipt_latex(tc_number, st_number, random_date, amex_number)

    # Compile the receipt to PNG
    compile_latex_to_png()

    # Clean up auxiliary files
    for ext in ["aux", "log", "pdf", "tex"]:
        if os.path.exists(f"receipt.{ext}"):
            os.remove(f"receipt.{ext}")

    print("Receipt generated: receipt.png")


if __name__ == "__main__":
    main()
