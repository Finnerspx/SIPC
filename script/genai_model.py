import json

import google.generativeai as genai

def user_engagement_playlist(model):
    conv_history = []
    state = "waiting_for_description" #Initial State


    while True:
        if state == "waiting_for_description":
            prompt = """
            You love everything music! Its your passion to work with people and create the best playlist(s) for them. Please engage with the user to get the right information to create the playlist they want. 
            
            """
            if conv_history:
                prompt = "\n".join(conv_history) + "\n" + prompt

            response = model.generate_content(prompt)
            print(response.text)
            conv_history.append(prompt)
            conv_history.append(response.text)
            user_input = input("User: ")
            conv_history.append("User: " + user_input)

            extracted_data = model.generate_content(f"""
            {conv_history[-3:]}
            Extract the playlist description from the user input.
            return the description only.
            """)

            playlist_description = extracted_data.text
            # process the playlist description with the gemini function created in the previous answer.
            parsed_data = parse_model_response(create_prompt_for_model(playlist_description))


            if parsed_data:
                #Code to create the playlist using the parsed data
                print("Creating playlist...")
                print("Playlist created!")
                return parsed_data
            else:
                print("Could not do it try again")

        elif state == "confirming_creation":
            # Code to confirm playlist creation with the user
            pass
        elif state == "done":
            print("hi")
            break
        else:
            print(f"Invalid state:  {state}")



def create_prompt_for_model(user_input):
    prompt = f"""
    Analyse the user's request for a Spotify playlist and extract parameters suitable for the Spotify API's recommendation engine. Provide output as a JSON object. 

    Examples:
    User Request: "A chill playlist for studying"
    JSON: {{"seed_genres": ["chill", "ambient"], "target_audio_features": {{"instrumentals": 0.7}}, "seed_artists":[],"seed_tracks":[], "keywords":[], "negative_keywords":[]}}
    
    User Request: "Energetic workout music with 90s hip-hop"
    JSON: {{"seed_genres": ["hip-hop"], "seed_artists": ["artists of 90s hip-hop"], "target_audio_features": {{"energy": 0.8, "danceability": 0.7}}, "seed_tracks":[], "keywords":[], "negative_keywords":[]}}

    User Request: "{user_input}"
    
    Analyze the request and provide the JSON output:

"""
    return prompt

def get_response_from_model(user_input, model):
    prompt = create_prompt_for_model(user_input)
    response = model.generate_content(prompt)
    return response.text


def parse_model_response(response_text):
    try:
        data = json.loads(response_text)
        return data
    except json.JSONDecodeError:
        print("Error: Invalid Json response")
        return None