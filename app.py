from flask import Flask, render_template, url_for, request, redirect, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from pyswip import Prolog
import requests
from bs4 import BeautifulSoup
import subprocess
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.secret_key = "supersecretkey"  # For session usage
db = SQLAlchemy(app)
app.app_context().push()

RESCUEGROUPS_API_KEY = "SP1Mg1Jg"

# Initialize Prolog
prolog = Prolog()
prolog.consult("pet_traits.pl")

# Questions for the Quiz
QUESTIONS = [
    {'id': 1, 'question': 'Would you consider yourself high energy, calm, or somewhere in the middle?',
     'options': [
        {'id': 1, 'option': 'High Energy'},
        {'id': 2, 'option': 'Calm'},
        {'id': 3, 'option': 'Neutral'}
    ]},
    {'id': 2, 'question': 'Do you or someone in your home have allergies?', 
     'options': [
        {'id': 1, 'option': 'Yes'},
        {'id': 2, 'option': 'No'},
    ]},
    {'id': 3, 'question': 'What type of home do you have?', 
     'options': [
        {'id': 1, 'option': 'Apartment'},
        {'id': 2, 'option': 'House with a Yard'},
        {'id': 3, 'option': 'House without Yard'},
    ]},   
    {'id': 4, 'question': 'Do you have small children?', 
     'options': [
        {'id': 1, 'option': 'Yes'},
        {'id': 2, 'option': 'No'},
    ]}, 
    {'id': 5, 'question': 'Do you have a preference for cats or dogs?', 
     'options': [
        {'id': 1, 'option': 'Cat'},
        {'id': 2, 'option': 'Dog'},
        {'id': 3, 'option': 'No preference'},
    ]},
    {'id': 6, 'question': 'Do you have a preference animal age?', 
     'options': [
        {'id': 1, 'option': 'Baby'},
        {'id': 2, 'option': 'Young'},
        {'id': 3, 'option': 'Senior'},
        {'id': 4, 'option': 'No preference'},
    ]},      
    {'id': 7, 'question': 'Have you cared for a pet before?', 
     'options': [
        {'id': 1, 'option': 'Yes'},
        {'id': 2, 'option': 'No'},
    ]}, 
    {'id': 8, 'question': 'Are you willing to train a new animal?', 
     'options': [
        {'id': 1, 'option': 'Yes'},
        {'id': 2, 'option': 'No'},
    ]},             
    {'id': 9, 'question': 'What is your current Zip Code?',
     'options': []  # No predefined options; user will type input
    },
]

@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('index.html')
    
@app.route('/quiz/<int:question_id>', methods=['GET', 'POST'])
def quiz(question_id):
    #Get the current question
    current_question = next((q for q in QUESTIONS if q['id'] == question_id), None)
    if not current_question:
        # If there are no more questions, then just return quiz results
        return redirect(url_for('results'))
    
    if request.method == 'POST':
        # If current_question has options, user selects one.
        # If not (like for the zip code), user will enter a text input.
        if current_question['options']:
            selected_option_id = int(request.form['option'])
            selected_option_text = next(o['option'] for o in current_question['options'] if o['id'] == selected_option_id)
        else:
            # No options, directly read text input (e.g., zip code)
            selected_option_text = request.form['option']

         # Debugging session before update
        # print("Session before update:", session.get('answers', {}))

        # Store the answer in session
        if 'answers' not in session:
            session['answers'] = {}

        session['answers'].update({f'q{question_id}': selected_option_text.lower()})
        session.modified = True

        # Debugging session after update

        # print("Session after update:", session.get('answers'))

        return redirect(url_for('quiz', question_id=question_id + 1))

    return render_template('quiz.html', question=current_question, total=len(QUESTIONS))



# @app.route('/results')
# def results():

#     ###formatting input answers for API
#     answers = session.get('answers', {})
#     energy = answers.get('q1')
#     if energy=="high energy":
#         energy="high_energy"
#     elif energy=="calm":
#         energy="calm"
#     else:
#         energy="neutral"
    
#     allergies = answers.get('q2')
#     if allergies == "Yes":
#         allergy_value = "allergies"
#     else:
#         allergy_value="no_allergies"

#     living = answers.get('q3')
#     living=living.split()[0]
#     if living=="House with a Yard":
#         yard="yes"
#     else:
#         yard="no"

#     small_children = answers.get('q4')
#     if small_children == "yes":
#         children_status = "small_children"
#     else:
#         children_status = "no_children"

#     preference_animal = answers.get('q5')
#     if preference_animal=="no preference":
#         preference_animal="no_preference"

#     preference_age = answers.get('q6')
#     if preference_age=="no preference":
#         preference_age="no_preference"

#     pet_experience = answers.get('q7')
#     if pet_experience=="Yes":
#         pet_experience="experienced"
#     else:
#         pet_experience="beginner"
    
#     train_preference = answers.get('q8')
#     if train_preference=="no":
#         train_preference="not_willing"
#     else:
#         train_preference="willing"

#     zipcode = answers.get('q9')

#     # Query Prolog for matching pets based on user preferences
#     query = f"""
#         user_pet(Pet, {allergy_value}, {children_status}, {preference_animal}, {living}, {yard}, {preference_age}, {pet_experience}, {train_preference}, {energy}),
#         pet(Pet, Temperament, Shedding, Size, Age, Training),
#         PetFact = pet(Pet, Temperament, Shedding, Size, Age, Training), !.
#     """

#     result = subprocess.run(
#         ["swipl", "-q", "-s", "pet_traits.pl", "-g", query, "-t", "halt"],
#         stdout=subprocess.PIPE,
#         text=True
#     )

#     # Capture the output from `write/1`
#     explanation = result.stdout.strip()
    
#     results = list(prolog.query(query))
#     if results:
#         pet_type=results[0]['Pet'][:3]
#         temperament=results[0]['Temperament']
#         shedding=results[0]['Shedding']
#         size=results[0]['Size']
#         age=results[0]['Age']
#         training=results[0]['Training']
            

#         print(f"pet({results[0]['Pet']}, {results[0]['Temperament']}, {results[0]['Shedding']}, {results[0]['Size']}, {results[0]['Age']}, {results[0]['Training']}).")
#     else:
#         print("Sorry, no pets match your preferences.")
    
#     ###Adjust terms for API input
#     if pet_type=="cat":
#         temperament=None
#     elif temperament=="high_energy":
#         temperament="High"
#     elif temperament=="calm":
#         temperament="Low"
#     else:
#         temperament="Moderate"
#     if shedding=="no_shed":
#         shedding="Low"
#     else:
#         shedding=None
#     if train_preference=="not_willing":
#         training=True
#     else:
#         training=None
#     if size=="small":
#         size=["Small","Medium"]
#     else:
#         size=["Large","X-Large"]
    
#     print(f"pets = query_pets_from_api(size: {size}, pet_type: {pet_type}, temperament: {temperament}, shedding: {shedding}, age: {age}, training: {training}, '92701')")
#     pets = query_pets_from_api(size, pet_type, shedding, age, training, temperament, zipcode)

#     first_pet = pets[0] if pets else None
 
#     return render_template('results.html', recommended_pet=first_pet, pets=pets, first_pet=first_pet, explanation=explanation, results=results)

@app.route('/results')
def results():

    ### Formating user input for the Prolog queries
    answers = session.get('answers', {})
    energy = answers.get('q1', 'neutral').lower().replace(' ', '_')    
    allergy_value = "allergies" if answers.get('q2', 'no') == 'yes' else "no_allergies"
    living = answers.get('q3').split()[0].lower()
    yard = "yes" if living == "House with a Yard" else "no"
    children_status = "small_children" if answers.get('q4', 'no') == 'yes' else "no_children"
    preference_animal = "no_preference" if answers.get('q5', 'no preference') == "no preference" else answers.get('q5', 'no preference').replace(' ', '_')
    preference_age = "no_preference" if answers.get('q6', 'no preference') == "no preference" else answers.get('q6', 'no preference').replace(' ', '_')
    pet_experience = "experienced" if answers.get('q7') == "Yes" else "beginner"
    train_preference = 'willing' if answers.get('q8', 'yes') == 'yes' else 'not_willing'
    zipcode = answers.get('q9')

    print("User Inputs:", {
        'allergy_value': allergy_value,
        'children_status': children_status,
        'preference_animal': preference_animal,
        'living': living,
        'yard': yard,
        'preference_age': preference_age,
        'pet_experience': pet_experience,
        'train_preference': train_preference,
        'energy': energy
    })

    # adds pets that are in range into the knowledge base
    api_pets = assert_pets_into_prolog(zipcode)

    # Use the formatted input to query Prolog for matches
    queries = [
        # Most specific queries
        f"user_pet(Pet, {allergy_value}, {children_status}, _, _, _, {preference_age}, {pet_experience}, {train_preference}, {energy}).",
        f"user_pet(Pet, {allergy_value}, {children_status}, _, _, _, _, {pet_experience}, {train_preference}, {energy}).",

        # Relaxing `pet_experience`
        f"user_pet(Pet, {allergy_value}, {children_status}, _, _, _, {preference_age}, _, {train_preference}, {energy}).",
        f"user_pet(Pet, {allergy_value}, {children_status}, _, _, _, _, _, {train_preference}, {energy}).",

        # Relaxing everything except `energy` and `children_status`
        f"user_pet(Pet, {allergy_value}, _, _, _, _, {preference_age}, _, _, {energy}).",
        f"user_pet(Pet, _, {children_status}, _, _, _, _, _, _, {energy}).",
        f"user_pet(Pet, _, _, _, _, _, _, _, _, {energy})."
    ]


    matched_pets = []

    for query in queries:
        print(f"Running Prolog query: {query}")  # Print the query being executed
        results = list(prolog.query(query))  # Execute the Prolog query
        print(f"Results for query: {results}")  # Print the results
        if results:
            matched_pets.extend(results)
            break  # Stop at the first query that returns results

     # If no Prolog matches, return early
    if not results:
        return render_template('results.html', recommended_pet=None, pets=[], explanation="No pets match your preferences.")

    result = subprocess.run(
        ["swipl", "-q", "-s", "pet_traits.pl", "-g", query, "-t", "halt"],
        stdout=subprocess.PIPE,
        text=True
    )

    # Capture the output from `write/1`
    explanation = result.stdout.strip()
    matched_pets = []
    ids = []

    # Process Prolog results and fetch details using query_pet_by_id
    for result in results:
        # Convert pet ID from bytes to a regular string if it's a byte string
        pet_id = result.get('Pet')
        if pet_id in ids:
            continue
        else: 
            ids.append(pet_id)
            
        if isinstance(pet_id, bytes):  # Check if it's a byte string
            pet_id = pet_id.decode('utf-8')   

        # Fetch pet details from the API
        pet_details = query_pet_by_id(pet_id)
        matched_pets.append(pet_details)

    # Debugging: Log matched pets
    print("Matched Pets:", matched_pets)

    first_pet = matched_pets[0] if matched_pets else None
 
    return render_template('results.html', recommended_pet=first_pet, pets=matched_pets, explanation=explanation, results=results)

def escape_prolog_string(value):
    """Escapes special characters in a string for Prolog."""
    if not value:
        return "unknown"
    # Escape double quotes and ensure the string is wrapped in double quotes
    escaped_value = value.replace('"', '\\"')
    escaped_value = escaped_value.replace("'", "''")
    return f'"{escaped_value}"'

def normalize_temperament_level(activity_level):
    if activity_level == "Highly Active":
        return "high_energy"
    elif activity_level == "Moderately Active":
        return "neutral"
    elif activity_level == "Slightly Active":
        return "calm"
    elif activity_level == "Not Active":
        return "calm"  
    else:
        return "neutral"

def normalize_shedding_level(shedding):
    if shedding == "None":
        return "low"
    elif shedding == "Moderate":
        return "moderate"
    elif shedding == "High":
        return "high"
    else:
        return "moderate" #accounts for unknown shedding
    
def assert_pets_into_prolog(zipcode):
    api_pets = query_by_zipcode(zipcode)

    # Clear existing facts
    prolog.retractall("pet(_, _, _,_,_,_)")

    for pet in api_pets:
        pet_id = escape_prolog_string(pet.get('pet_id', 'unknown'))
        temperament = normalize_temperament_level(pet.get('temperament', 'unknown'))
        shedding = normalize_shedding_level(pet.get('shedding', 'unknown'))
        size = pet.get('size', 'unknown').lower().replace(' ', '_')
        age = pet.get('age', 'unknown').lower().replace(' ', '_')
        training = 'trained' if pet.get('training', False) else 'no_trained'

        fact = f"pet({pet_id}, {temperament}, {shedding}, {size}, {age}, {training})"

        # Print the fact for debugging
        print(f"Generated Prolog fact: {fact}")

        try:
            prolog.assertz(fact)
        except Exception as e:
            print(f"Error asserting fact: {fact}\nCaused by: {e}")

    print("asserts function")
    print(list(Prolog.query("pet(A, B, C, D, E, F)")))
    return api_pets

@app.route('/browse', methods=['GET'])
def browse():
    # Example data
    species_list = ['Dog', 'Cat', 'Rabbit']
    breed_list = ['Labrador', 'Siamese', 'Rex']
    age_list = ['Puppy', 'Kitten', 'Adult']
    
    # Capture filter parameters from the request
    selected_species = request.args.get('species')
    selected_breed = request.args.get('breed')
    selected_age = request.args.get('age')

    # Fetch pets from the API based on filters
    pets = query_pets_from_api_general(selected_species, selected_breed, selected_age)

    return render_template(
        'browse.html',
        species_list=species_list,
        breed_list=breed_list,
        age_list=age_list,
        pets=pets
    )

def query_by_zipcode(zipcode):
    url = "https://api.rescuegroups.org/v5/public/animals/search/available/haspic"
    headers = {
        'Content-Type': 'application/vnd.api+json',
        'Authorization': RESCUEGROUPS_API_KEY
    }

    payload = {
        "data": {
            "filterRadius": {
                "miles": 50,  # Adjust the radius if needed
                "postalcode": zipcode
            }
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

        pets = []
        for animal in data.get('data', []):
            attributes = animal.get('attributes', {})
            pets.append({
                'name': attributes.get('name', 'Unknown name'),
                'breed': attributes.get('breedPrimary', 'Unknown breed'),
                'age': attributes.get('ageGroup', 'Unknown age'),
                'gender': attributes.get('sex', 'Unknown gender'),
                'location': attributes.get('citystate', 'Unknown location'),
                'image_url': attributes.get('pictureThumbnailUrl', 'No image available'),
                'pet_id': animal.get('id', 'Unknown ID'),
                'temperament': attributes.get('activityLevel', 'Unknown temperament'),
                'size': attributes.get('sizeGroup', 'Unknown size'),
                'training': attributes.get('isHousetrained', False),
                'shedding': attributes.get('sheddingLevel', 'Unknown shedding'),
                'isMicrochip': attributes.get('isMicrochipped', False),
                'isVaccinated': attributes.get('isCurrentVaccinations', False)          
            })
        return pets

    except requests.RequestException as e:
        print(f"Error querying the API: {e}")
        return []


def query_pets_from_api_general(species=None, breed=None, age=None):
    url = "https://api.rescuegroups.org/v5/public/animals/search/available/haspic"
    headers = {
        'Content-Type': 'application/vnd.api+json',
        'Authorization': RESCUEGROUPS_API_KEY
    }

    # Build the filter payload dynamically based on available parameters
    filters = []
    if species:
        filters.append({"fieldName": "animals.species", "operation": "equal", "criteria": species})
    if breed:
        filters.append({"fieldName": "animals.breedPrimary", "operation": "equal", "criteria": breed})
    if age:
        filters.append({"fieldName": "animals.ageGroup", "operation": "equal", "criteria": age})

    payload = {
        "data": {
            "filters": filters,
            "filterProcessing": "1"
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

        pets = []
        for animal in data.get('data', []):
            attributes = animal.get('attributes', {})
            pets.append({
                'name': attributes.get('name', 'Unknown name'),
                'breed': attributes.get('breedPrimary', 'Unknown breed'),
                'age': attributes.get('ageGroup', 'Unknown age'),
                'gender': attributes.get('gender', 'Unknown gender'),
                'location': attributes.get('citystate', 'Unknown location'),
                'image_url': attributes.get('pictureThumbnailUrl', 'No image available'),
                'pet_id': animal.get('id', 'Unknown ID')
            })
        return pets

    except requests.RequestException as e:
        print(f"Error querying the API: {e}")
        return []

@app.route('/pet/<pet_id>')
def profile(pet_id):
    pet = query_pet_by_id(pet_id)

    if not pet:
        return render_template('error.html', message="Pet not found."), 404

    return render_template('profile.html', pet=pet)

def query_pet_by_id(pet_id):
    url = f"https://api.rescuegroups.org/v5/public/animals/{pet_id}"
    headers = {
        'Content-Type': 'application/vnd.api+json',
        'Authorization': RESCUEGROUPS_API_KEY
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        # Log API response for debugging
        print("API Response Data:", data)

        pet_data = data.get('data')
        if isinstance(pet_data, list):
            # If data is a list, take the first element
            pet_data = pet_data[0] if pet_data else None

        if not pet_data:
            print("No pet data found.")
            return None

        attributes = pet_data.get('attributes', {})
        if not attributes:
            print("No attributes found for this pet.")
            return None
        
        # Safely parse the description
        description_html = attributes.get('description', '')
        if description_html:
            soup = BeautifulSoup(description_html, 'html.parser')
            description = soup.get_text().strip()
        else:
            description = "No description available."

        return {
            'name': attributes.get('name', 'Unknown name'),
            'breed': attributes.get('breedPrimary', 'Unknown breed'),
            'age': attributes.get('ageGroup', 'Unknown age'),
            'gender': attributes.get('sex', 'Unknown gender'),
            'location': attributes.get('citystate', 'Unknown location'),
            'image_url': attributes.get('pictureThumbnailUrl', 'No image available'),
            'pet_id': pet_data.get('id', 'Unknown ID'),
            'temperament': attributes.get('activityLevel', 'Unknown temperament'),
            'size': attributes.get('sizeGroup', 'Unknown size'),
            'training': attributes.get('isHousetrained', False),
            'shedding': attributes.get('sheddingLevel', 'Unknown shedding'),
            'isMicrochip': attributes.get('isMicrochipped', False),
            'isVaccinated': attributes.get('isCurrentVaccinations', False)   
        }

    except requests.RequestException as e:
        print(f"Error querying the API: {e}")
        return None

def generate_filter_string(x):

  filter_string = ""
  for i in range(1, x + 1):
    filter_string += str(i)
    if i < x:
      filter_string += " AND "
  return filter_string

def query_pets_from_api(size, pet_type, shedding, age, training, temperament, zipcode):
    url = "https://api.rescuegroups.org/v5/public/animals/search/available/haspic"
    headers = {
        'Content-Type': 'application/vnd.api+json',
        'Authorization': RESCUEGROUPS_API_KEY
    }

    # Build the filter payload dynamically based on available parameters
    filters = []
    if pet_type:
        filters.append({"fieldName": "species.singular", "operation": "equals", "criteria": pet_type})
    if age:
        filters.append({"fieldName": "animals.ageGroup", "operation": "equal", "criteria": age})
    if size:
        filters.append({"fieldName": "animals.sizeGroup", "operation": "equal", "criteria": size})
    if temperament:
        filters.append({"fieldName": "animals.energyLevel", "operation": "equal", "criteria": temperament})
    if shedding:
        filters.append({"fieldName": "animals.groomingNeeds", "operation": "equal", "criteria": shedding})
    if training:
        filters.append({"fieldName": "animals.isHousetrained", "operation": "equal", "criteria": training})

    for x in filters:
        print(x)

    filter_string = generate_filter_string(len(filters))

    payload = {
        "data": {
            "filters": filters,
            "filterProcessing": filter_string,
            "filterRadius": {
                "miles": 1000,
                "postalcode": zipcode
            }
        }
    }

    try:
        # Log headers and payload for debugging
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        print(f"Error querying the API: {e}")
        data = {'data': [], 'included': []}

    # Create a mapping for location IDs to city names
    location_mapping = {}
    for included_item in data.get('included', []):
        if included_item['type'] == 'locations':
            location_id = included_item['id']
            city = included_item.get('attributes', {}).get('city', 'Unknown city')
            location_mapping[location_id] = city

    pets = []

    for animal in data.get('data', []):
        attributes = animal.get('attributes', {})
        relationships = animal.get('relationships', {})
        description_html = attributes.get('descriptionHtml', 'No description available')

        # Extract the location ID from relationships
        location_data = relationships.get('locations', {}).get('data', [])
        location_id = location_data[0]['id'] if location_data else None
        city = location_mapping.get(location_id, 'Unknown city')

        # Parse the HTML description
        soup = BeautifulSoup(description_html, 'html.parser')
        description = soup.get_text().strip()

        pets.append({
            'name': attributes.get('name', 'Unknown name'),
            'breed': attributes.get('breedPrimary', 'Unknown breed'),
            'age': attributes.get('ageGroup', 'Unknown age'),
            'gender': attributes.get('sex', 'Unknown gender'),
            'city': city,
            'description': description,
            'pet_id': animal.get('id', 'Unknown ID'),
            'image_url': attributes.get('pictureThumbnailUrl', 'No image available'),
            'url': attributes.get('url', 'No URL available')
        })

    return pets

if __name__ == "__main__":
    app.run(debug=True)
