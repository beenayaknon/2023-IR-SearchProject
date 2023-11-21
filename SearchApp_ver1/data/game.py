import json

# Load the JSON 
with open('C:/bibiworksp/IR Project/Ex.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Open a new JSON file in write mode for newline-delimited JSON output
with open('output.json', 'w', encoding='utf-8') as output_file:
    # Iterate through the "example" array and write each game as newline-delimited JSON
    for game_data in data['example']:
        game = {
            "name_original": game_data["name_original"],
            "description": game_data["description"],
            "genres": [genre["name"] for genre in game_data["genres"]],
            "platform": [platform["platform"]["name"] for platform in game_data["platforms"]],
            "developers": [developer["name"] for developer in game_data["developers"]],
            "publishers": [publisher["name"] for publisher in game_data["publishers"]],
            "tags": [tag["name"] for tag in game_data["tags"]],
            "background_image": game_data["background_image"],
            "background_image_additional": game_data["background_image_additional"]
        }
        # Write each game object as a newline-delimited JSON entry
        output_file.write(json.dumps(game, ensure_ascii=False))
        output_file.write('\n')

#yhea!!!! new file
