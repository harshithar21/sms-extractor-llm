"""
Synthetic Indian bank/UPI SMS generator.
Each example = (sms text, ground-truth JSON). Labels are correct by construction.

NOTE: templates are modelled on common SMS styles, NOT copied from any real bank.
Later, replace/add templates by copying the *structure* of your own real SMS.
"""
import json, random
from datetime import date, timedelta

random.seed(42)

MERCHANTS = ["swiggy", "zomato", "amazon", "flipkart", "bigbasket", "uber", "ola",
             "irctc", "jio", "airtel", "bookmyshow", "myntra", "blinkit", "zepto"]
HANDLES = ["ybl", "okaxis", "oksbi", "okhdfcbank", "paytm", "ibl", "axl"]
NAMES = ["RAHUL SHARMA", "PRIYA NAIR", "AMIT PATEL", "SNEHA REDDY", "KARTHIK IYER",
         "ANJALI GUPTA", "MOHAMMED ASIF", "DIVYA KRISHNAN", "ROHAN MEHTA", "LAKSHMI DEVI"]
COMPANIES = ["INFOSYS LTD", "TCS LTD", "WIPRO LTD", "ZOHO CORP", "ACME TECH PVT LTD"]

def rand_amount():
    return round(random.choice([random.uniform(10, 500), random.uniform(500, 5000),
                                random.uniform(5000, 80000)]), random.choice([0, 2, 2]))

def fmt_amount(a):
    style = random.choice(["Rs.{:.2f}", "Rs {:.2f}", "INR {:,.2f}", "Rs.{:,.2f}"])
    return style.format(a)

def fmt_date(d):
    style = random.choice(["%d-%b-%y", "%d/%m/%y", "%d-%m-%Y", "%d%b%y"])
    return d.strftime(style)

def ref():
    return str(random.randint(10**11, 10**12 - 1))

def acc():
    return f"{random.randint(0, 9999):04d}"

def make_example():
    a = rand_amount()
    d = date(2025, 1, 1) + timedelta(days=random.randint(0, 600))
    ac = acc()
    bal = round(random.uniform(100, 250000), 2)
    A, B, D = fmt_amount(a), fmt_amount(bal), fmt_date(d)
    kind = random.choice(["upi_debit_bal", "upi_debit_nobal", "upi_credit", "card",
                          "atm", "neft_credit", "imps_debit", "emi"])
    merchant = random.choice(MERCHANTS)
    vpa = f"{merchant}@{random.choice(HANDLES)}"
    person = random.choice(NAMES)

    if kind == "upi_debit_bal":
        sms = f"{A} debited from A/c XX{ac} on {D} to VPA {vpa} (UPI Ref No {ref()}). Bal: {B}"
        y = dict(type="debit", mode="UPI", counterparty=merchant, balance=bal)
    elif kind == "upi_debit_nobal":
        sms = (f"Dear Customer, {A} has been debited from your a/c ending {ac} on {D} "
               f"towards UPI/{vpa}. Ref {ref()}. Not you? Call bank helpline.")
        y = dict(type="debit", mode="UPI", counterparty=merchant, balance=None)
    elif kind == "upi_credit":
        sms = f"{A} credited to A/c XX{ac} on {D} from {person} (UPI Ref {ref()}). Avl Bal {B}"
        y = dict(type="credit", mode="UPI", counterparty=person, balance=bal)
    elif kind == "card":
        sms = f"Spent {A} on Card XX{ac} at {merchant.upper()} on {D}. Not you? Block card now."
        y = dict(type="debit", mode="CARD", counterparty=merchant, balance=None)
    elif kind == "atm":
        sms = f"{A} withdrawn from ATM on {D} using Card XX{ac}. Avl Bal {B}"
        y = dict(type="debit", mode="ATM", counterparty=None, balance=bal)
    elif kind == "neft_credit":
        co = random.choice(COMPANIES)
        sms = f"A/c XX{ac} credited with {A} on {D} by NEFT from {co}. Ref {ref()}. Bal {B}"
        y = dict(type="credit", mode="NEFT", counterparty=co, balance=bal)
    elif kind == "imps_debit":
        sms = f"{A} sent from A/c XX{ac} to {person} via IMPS on {D}. Ref {ref()}. Bal {B}"
        y = dict(type="debit", mode="IMPS", counterparty=person, balance=bal)
    else:  # emi
        sms = f"EMI of {A} debited from A/c XX{ac} on {D}. Ensure sufficient balance next month."
        y = dict(type="debit", mode="EMI", counterparty=None, balance=None)

    label = {"amount": a, "type": y["type"], "mode": y["mode"], "account_last4": ac,
             "date": d.isoformat(), "counterparty": y["counterparty"], "balance": y["balance"]}
    return {"sms": sms, "label": label}

def main(n=1500):
    data = [make_example() for _ in range(n)]
    random.shuffle(data)
    splits = {"train": data[:int(.8*n)], "val": data[int(.8*n):int(.9*n)], "test": data[int(.9*n):]}
    for name, rows in splits.items():
        with open(f"data/{name}.jsonl", "w") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(name, len(rows))

if __name__ == "__main__":
    main()
