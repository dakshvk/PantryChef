class Recipe:
    def __init__(self, name, cuisine,  ingredients, meal_type, calories=None):
        self.name = name #stores recipe name
        self.cuisine = cuisine #stores cuisine type
        self.ingredients = ingredients # stores the ingredients in the cusine
        self.meal_type = meal_type # stores what type of meal it would be
        self.calories = calories #stores the number of calories

    def __str__(self):
        return f'{self.name ({self.cuisine}) - self.meal_type}'

class PantryChef: #this construcotr initializes an empty list to hold all recipe objects
        #goal is to add recipes to this list using add_recipe method
    def __init__(self):
            self.recipes = []

    def add_recipe(self, recipe):
            self.recipes.append(recipe)

    def find_recipes(self, user_ingredients, cuisine_filter=None, meal_filter=None):
        matches = [] # empty list to store relative matches
            #goes through each recipe in collection
        for recipe in self.recipes: # calculate which ingredients match between recipe and user
            matching_ingredients = set(user_ingredients) & set(recipe.ingredients)
                #set() converts the lists to set so we can do mathematical ops later
            match_score = len(matching_ingredients) / len(recipe.ingredients)

                # cuisine filter if given cuisine
            if cuisine_filter.lower() and recipe.cuisine.lower() != cuisine_filter.lower():
                continue #skips to next recipe if user cuisine doesnt match recipes

            if meal.filter.lower() and recipe.meal_type.lower() != meal_filter.lower():
                continue
                #same with meal type filter aka breakfast lunch dinner snack and
            if match_score > 0: # creates match dictionary with recipe and percentage match
                    #want it to later display : 'hey you have x/y ingredients'
                matches.append({ 'recipe': recipe, 'match score': round(match_score * 100),
                    'matching_ingredients': list(matching_ingredients)
                                     }) # converts set back to list
        matches.sort(key=lambda x: x['match_score'], reverse=True)
                        # finally sorts matches score in order descending
        return matches


