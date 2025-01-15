import requests
from pprint import pprint

api_key = '201dc8eb3a5a4b348e640fd916161771'

def get_food_nutrition(food_name):
    # 构建搜索URL
    url = f'https://api.spoonacular.com/food/ingredients/search?query={food_name}&number=3&apiKey={api_key}'
    
    # 发送请求
    response = requests.get(url)
    data = response.json()
    
    if response.status_code == 200 and 'results' in data:
        products = data['results']
        pprint(products)
    else:
        print("Error: Could not retrieve product data.")

# 查询食物
food_name = 'pork'  # 你可以替换为任意食物名称
get_food_nutrition(food_name)
