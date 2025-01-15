import requests

# 输入您的 API 密钥
api_key = 'bvYZvGjAePpfoqGxLoLr4dHiVkfGcfWKE2cMm6Kb'

# 目标食物名称
food_name = 'apple'

# 请求 URL，进行食物搜索
url = f'https://api.nal.usda.gov/fdc/v1/foods/search?query={food_name}&api_key={api_key}'

# 发起请求并获取结果
response = requests.get(url)

# 如果请求成功
if response.status_code == 200:
    data = response.json()
    # 输出食物信息
    for food in data['foods']:
        print(f"Food: {food['description']}")
        print(f"FDC ID: {food['fdcId']}")
        # print(f"Food Group: {food['foodCategory']}")
        # print(f"Nutrients: {food['foodNutrients']}")
else:
    print("Error fetching data:", response.status_code)
