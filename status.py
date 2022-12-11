import requests
from bs4 import BeautifulSoup
import time
import json
import os
import smtplib


#login
with requests.Session() as c:
    url = 'url'
    USERNAME = 'email'
    PASSWORD = 'password'
    c.get(url)
    login_data = dict(username=USERNAME, password=PASSWORD, next='/')
    c.post(url, data=login_data, headers={"Referer": "url"})


#order status
def get_order_status(session, order_id):
    order_status_resp = session.get(f"url{order_id}")
    soup = BeautifulSoup(order_status_resp.text, "html.parser")

    items = soup.find_all("div", {"class": "orderreviewitem"})
    
    for item in items:
        title = item.find("div", {"class": "reviewtitle"}).text
        status = item.find("img", {"class": "orderlinestatus"})["alt"]

        if status == "Waiting to Process":
            status = "❌"
        elif status == "Picked and Scanned":
            status = "✅"
        elif status == "Shipped":
            status = "📦"
        
    return title, status

def get_orders(session):
    orders_resp = session.get("url")
    soup = BeautifulSoup(orders_resp.text, "html.parser")

    orders = soup.find_all("tr", {"class": "orderitem"})
    
    orders_to_check = {}

    incomplete_orders = []
    for order in orders:
        if order.find("a", {"class": "trackingid"}):
            continue
        incomplete_orders.append(order)

    for order in incomplete_orders:
        order_id = order.find("a", {"class": "action"}).text
        title, status = get_order_status(session, order_id)
        
        orders_to_check[order_id] = {
            "title": title,
            "status": status
        }

    return orders_to_check
    

# if the status of an order changes, return a list of orders that have changed
def compare_order_status(old_order_status, new_order_status):
    changed_orders = []

    for order_id, order in new_order_status.items():
        if old_order_status[order_id]["status"] != order["status"]:
            changed_orders.append(f"{order_id} - {order['title']} - {order['status']}")

    return changed_orders

#email
def send_email(changed_orders):
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(username, password)
    message = "Order has Changed"
    s.sendmail("sender email", "receiver email")
    s.quit()

def load_order_status():
    try:
        with open("order_status.json", "r") as f:
            return json.load(f)
    except:
        return None

# save order status to file
def save_order_status(order_status):
    with open("order_status.json", "w") as f:
        json.dump(order_status, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    session = requests.Session()

time.sleep(60*5)
