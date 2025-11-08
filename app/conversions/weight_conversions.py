from bs4 import BeautifulSoup
import requests

url = "https://www.kingarthurbaking.com/learn/ingredient-weight-chart"  # Replace with your target URL
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
