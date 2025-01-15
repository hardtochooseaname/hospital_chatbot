import requests
from pprint import pprint

# 输入您的 API 密钥
api_key = 'bvYZvGjAePpfoqGxLoLr4dHiVkfGcfWKE2cMm6Kb'

# 目标食物名称
food_name = 'apple'
fdcid = "2709215"

# 请求 URL，进行食物搜索
url = f'https://api.nal.usda.gov/fdc/v1/food/{fdcid}?api_key={api_key}'


# 发起请求并获取结果
response = requests.get(url)

# 如果请求成功
if response.status_code == 200:
    food_data = response.json()
    #pprint(food_data)
    # 提取食物描述
    food_description = food_data["description"]

    # 提取食物营养成分并格式化
    nutrients = food_data["foodNutrients"]
    formatted_nutrients = "\n".join([f"{nutrient['nutrient']['name']}: {nutrient['nutrient']['number']} {nutrient['nutrient']['unitName']}" for nutrient in nutrients])

    # 将描述和营养成分数据组合成可以传递给LLM的字符串
    formatted_string = f"Food Description: {food_description}\n\nNutritional Information:\n{formatted_nutrients}"

    # 输出最终字符串
    print(formatted_string)
else:
    print("Error fetching data:", response.status_code)
