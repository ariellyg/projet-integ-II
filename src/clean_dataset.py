from pathlib import Path 
import pandas as pd
import os 

data_path = Path('data')
dataset_path = data_path / 'test_recipes.csv'
clean_dataset_path = data_path / 'format_test_recipes.csv'

def format_recipe(row):
    """Formats a row of the dataset into a recipe string"""
    name = row["Name"]
    ingredients = [item['name'] for item in eval(row["Ingredients"])]
    directions = " ".join(eval(row["Directions"]))
    
    full_text = f"Recipe: {name}\nIngredients: {', '.join(ingredients)}\nInstructions: {directions}"
    return full_text

def format_dataset():
    """Apply the format_recipe function to each row of the dataset"""
    df = pd.read_csv(dataset_path)
    df["full_text"] = df.apply(format_recipe, axis=1)
    df = df['full_text']
    df.to_csv(clean_dataset_path, index=False)

format_dataset()