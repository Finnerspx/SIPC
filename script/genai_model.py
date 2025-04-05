import json
import re

import google.generativeai as genai

def user_engagement_take2(model):
    """
    Engages the user to get playlist details and returns JSON data.
    :param model:
    :return:
    """
    conversation_history = []
    print("Beats: Thinking of how to start....")
    initial_prompt = "You are a friendly and enthusiastic music AI. Your name is 'Beats'. Start a short, welcoming conversation with the user by introducing yourself. Your job and passion is to work with people to create the best playlist(s) for them. Please engage with the user to get the right information to create the playlist they want."
    try:
        initial_response = model.generate_content(initial_prompt)
        greeting = initial_response.text.strip()
        print(f"Beats: {greeting}")
        conversation_history.append(f"Beats: {greeting}")
    except Exception as e:
        fallback_greeting = "Hi there! I am your music AI assistant, Beats! I can help you create a Spotify playlist. What kind of music are you in the mood for?"
        conversation_history.append(f"AI: {fallback_greeting}")
        print(f"Warning: Initial greeting generation failed, using fallback. Error: {e}")

    while True:
        user_input = input("User: ")
        conversation_history.append("User: " + user_input)

        #Attempt to structure latest input into JSON
        json_prompt = create_prompt_for_model(user_input)

        #Call Helper function to get and parse the JSON
        parsed_data = parse_model_response_new(model, json_prompt)

        if parsed_data:
            #Success! Structured JSON
            print("Great!")
            return parsed_data
        else:
            recent_history = "\n".join(conversation_history[-6:1])
            print(recent_history)
            clarification_prompt = f"""
            You are a friendly and enthusiastic music AI. Your name is 'Beats'. You are trying to understand a user's playlist request.
            An attempt to structure their previous request into JSON format failed.
            Based on the recent conversation history below, ask a friendly, specific, and concise question to clarify what kind of playlist they want. Focus on asking about genre, mood, specific artists, activity, or era. Avoid generic phrases like "Tell me more".

            Recent Conversation History:
            {recent_history}

            Ask your single clarifying question now:
            """
        try:
            clarification_response = model.generate_content(clarification_prompt)
            clarification_response_text = clarification_response.text.strip()
            print(f"Beats: {clarification_response_text}")
            conversation_history.append("Beats: " + clarification_response_text)
        except Exception as e:
            fallback_clarification = "Could you perhaps tell me more about the genre, mood, or artists you have in mind?"
            print(f"Beats: There's been an issue fam {e}")
            conversation_history.append(f"Beats: {fallback_clarification}")

    # Loop continues, waiting for the user's next input after the clarifying question

def parse_model_response_new(model, json_prompt):

    try:
        print("Attempting to gen structured JSON")
        response = model.generate_content(json_prompt)

        # Clean up the response text to extract only the JSON part
        # Gemini might add explanations or backticks around the JSON
        json_text = response.text
        # Find the first '{' and the last '}'
        start_index = json_text.find('{')
        end_index = json_text.rfind('}')

        if start_index != -1 and end_index != -1 and end_index > start_index:
            json_string = json_text[start_index: end_index + 1]

            json_string = re.sub(r"//.*", "", json_string)


            print(f"Extracted JSON string: {json_string}")  # Debug print
            parsed_data = json.loads(json_string)
            print("Successfully parsed JSON.")  # Debug print
            return parsed_data
        else:
            print("Error: Could not find valid JSON structure in the response.")
            print(f"Full response was: {response.text}")
            return None

    except json.JSONDecodeError as e:
        print(f"Error: Failed to decode JSON from response: {e}")
        print(f"Response text was: {response.text}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during JSON parsing: {e}")
        print(f"Response text was: {response.text}")
        return None




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

                return parsed_data
            else:
                print("Could not do it try again")

        elif state == "confirming_creation":
            # Code to confirm playlist creation with the user
            print("Confirm")
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
    JSON: {{
        "seed_genres": ["chill", "ambient"],
        "seed_artists": [], #Could contain Spotify Artist IDs 
        "seed_tracks': [], #Could contain Spotify track IDs
        "target_audio_features": {{
            "energy": 0.3,
            "instrumentalness': 0.8,
            "valence": 0.4
        }},
        "keywords": ["focus", "study", "electronic"] # Keywords might be used for playlist name/desc
    }}
    
    User Request: "Energetic workout music with 90s hip-hop"
    JSON: {{
        "seed_genres": ["hip-hop"],
        "seed_artists": [], #Could contain Spotify Artist IDs 
        "seed_tracks": [], #Could contain Spotify track IDs
        "target_audio_features": {{
            "energy": 0.8,
            '"danceability": 0.7,
        }},
        "keywords": ["workout", "hype", "energy"] # Keywords might be used for playlist name/desc
    }}

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



