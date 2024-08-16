import requests
from bs4 import BeautifulSoup
import frappe
@frappe.whitelist()
def run_me():  
    # URL of the website
    url = 'https://www.l192.com/search?category_id=40'

    # Send a GET request to the website
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all div elements with the specific class
        products = soup.find_all('div', class_='ProductColumn-module_title__qh2oB')
        
        # Extract and print the data
        for product in products:
            print(product.text.strip())
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
