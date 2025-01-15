import requests
from pprint import pprint
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('SPOONNCULAR_API_KEY')

def get_food_id(food_name) -> list:
    # 构建搜索URL
    url = f'https://api.spoonacular.com/food/ingredients/search?query={food_name}&number=3&apiKey={api_key}'
    
    # 发送请求
    response = requests.get(url)
    data = response.json()
    
    print(f"API Calling: searching food id of {food_name}...")
    if response.status_code == 200 and 'results' in data:
        food = data['results'][0]
        return food['id'], food['name']
    else:
        print("API Calling Error: Could not retrieve food data.")
        return None 


def get_food_detail(food_id, food_name):
    # 构建搜索URL
    url = f'https://api.spoonacular.com/food/ingredients/{food_id}/information?amount=1&apiKey={api_key}'

    # 发送请求
    response = requests.get(url)
    data = response.json()
    
    print(f"API Calling: searching detailed infomation of {food_name}...")
    if response.status_code == 200:
        nutrients = data['nutrition']['nutrients']
        nutrient_info = "\n".join([
            f"  {item['name']}: {item['amount']}{item['unit']} ({item['percentOfDailyNeeds']}% of daily needs)"
            for item in nutrients
        ])
        food_datail = f"Food Name: {data['name']}\nNutritional Information:\n{nutrient_info}\n"
        return food_datail
    else:
        print(response.status_code)
        print("API Calling Error: Could not retrieve food data.")
        return ""

def get_food_nutrients_info(food_name):
    food_id, food_name = get_food_id(food_name)
    food_detail = get_food_detail(food_id, food_name)
    return food_detail
