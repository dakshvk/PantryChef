import requests

def test_api_connection():
    API_KEY = 'ec1abcfd4eec4b18ac592c09a770bd4a'

    url = f'https://api.spoonacular.com/recipes/findByIngredients?apiKey={API_KEY}'

    params = {
        'ingredients': 'chicken, rice, tomatoes',
        'number': 3,
        'apikey': API_KEY
    }
    print('Testing API connection...')
    print(f'Sending request to {url}...')
    print(f'Params: {params}')

    try:
        response = requests.get(url, params=params)
        # GET request to api
        if response.status_code == 200:
            print('API request successful')

            #converts json response to python data
            recipes = response.json()
            print(f'Data Got {len(recipes)} recipes:')
            # Displays each recipe recvied
            for i, recipe in enumerate(recipes, 1):
                print(f"\n{i}. {recipe['title']}")
                print(f' Image: {recipe["image"]}')
                print(f' Used Ingredients: {len(recipe["usedIngredients"])}')
                print(f' Missed Ingredients: {len(recipe["missedIngredients"])}')
            else:
                print(f' API Error: {response.status_code}')
                print(f' Message: {response.text}')
    except Exception as e:
        print(f' Something went wrong: {e}')

if __name__ == '__main__':
    test_api_connection()

