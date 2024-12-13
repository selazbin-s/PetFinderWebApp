from flask import Flask, render_template, url_for, request, redirect, jsonify, session, abort
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from pyswip import Prolog
from dotenv import load_dotenv
import requests
import html
import subprocess
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.secret_key = "supersecretkey"  # For session usage
db = SQLAlchemy(app)
app.app_context().push()

load_dotenv()
RESCUEGROUPS_API_KEY = os.getenv("API_KEY")

# Initialize Prolog
prolog = Prolog()
prolog.consult("pet_traits.pl")  # Load the Prolog file

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
    session.clear() 
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
        print("Session before update:", session.get('answers', {}))

        # Store the answer in session
        if 'answers' not in session:
            session['answers'] = {}

        session['answers'].update({f'q{question_id}': selected_option_text.lower()})
        session.modified = True

        return redirect(url_for('quiz', question_id=question_id + 1))

    return render_template('quiz.html', question=current_question, total=len(QUESTIONS))

@app.route('/results')
def results():

    # Retrieve answers from the session
    answers = session.get('answers', {})

    # Map and adjust terms for API input
    energy = answers.get('q1')
    if energy=="high energy":
        energy="high_energy"
    elif energy=="calm":
        energy="calm"
    else:
        energy="neutral"
    
    allergies = answers.get('q2')
    allergy_value = "allergies" if allergies == "Yes" else "no_allergies"

    living = answers.get('q3')
    living=living.split()[0]
    yard = "yes" if living == "House with a Yard" else "no"

    small_children = answers.get('q4')
    children_status = "small_children" if small_children == "yes" else "no_children"

    preference_animal = answers.get('q5')
    preference_animal = "no_preference" if preference_animal == "no preference" else preference_animal

    preference_age = answers.get('q6')
    preference_age = "no_preference" if preference_age == "no preference" else preference_age

    pet_experience = answers.get('q7')
    pet_experience = "experienced" if pet_experience == "Yes" else "beginner"
    
    train_preference = answers.get('q8')
    train_preference = "not_willing" if train_preference == "no" else "willing"

    zipcode = answers.get('q9')

    # Query Prolog for matching pets based on user preferences
    query = f"""
        user_pet(Pet, {allergy_value}, {children_status}, {preference_animal}, {living}, {yard}, {preference_age}, {pet_experience}, {train_preference}, {energy}),
        pet(Pet, Temperament, Shedding, Size, Age, Training),
        PetFact = pet(Pet, Temperament, Shedding, Size, Age, Training), !.
    """

    result = subprocess.run(
        ["swipl", "-q", "-s", "pet_traits.pl", "-g", query, "-t", "halt"],
        stdout=subprocess.PIPE,
        text=True
    )

    # Capture and clean up the output produced by the Prolog `write/1` predicate
    explanation = result.stdout.strip()
    
    # Execute the Prolog query and collect the results as a list of dictionaries
    results = list(prolog.query(query))

    # Check if the query returned any results
    if results:
        # Extract and process individual attributes from the first result
        pet_type=results[0]['Pet'][:3]
        temperment=results[0]['Temperament']
        shedding=results[0]['Shedding']
        size=results[0]['Size']
        age=results[0]['Age']
        training=results[0]['Training']
            
        print(f"pet({results[0]['Pet']}, {results[0]['Temperament']}, {results[0]['Shedding']}, {results[0]['Size']}, {results[0]['Age']}, {results[0]['Training']}).")
    else:
        print("Sorry, no pets match your preferences.")
    
    ###Adjust terms for API input
    if pet_type=="cat":
        temperment=None
    elif temperment=="high_energy":
        temperment="High"
    elif temperment=="calm":
        temperment="Low"
    else:
        temperment="Moderate"
    if shedding=="no_shed":
        shedding="Low"
    else:
        shedding=None
    if train_preference=="not_willing":
        training=True
    else:
        training=None
    if size=="small":
        size=["Small","Medium"]
    else:
        size=["Large","X-Large"]
    
    print(f"pets = query_pets_from_api(size: {size}, pet_type: {pet_type}, temperment: {temperment}, shedding: {shedding}, age: {age}, training: {training}, '92701')")
    pets = query_pets_from_api(size, pet_type, shedding, age, training, temperment, zipcode)

    first_pet = pets[0] if pets else None
 
    return render_template('results.html', pets=pets, first_pet=first_pet, explanation=explanation, results=results)

@app.route('/browse', methods=['GET'])
def browse():
    # List of filters
    species_list = ['Dog', 'Cat', 'Bird']
    age_list = ['Baby', 'Young Adult', 'Senior']
    
    # Capture filter parameters from the request
    selected_species = request.args.get('species')
    selected_age = request.args.get('age')

    # Fetch pets from the API based on filters
    pets = query_pets_from_api_general(selected_species, selected_age)

    return render_template(
        'browse.html',
        species_list=species_list,
        age_list=age_list,
        pets=pets
    )

def query_pets_from_api_general(species=None, age=None):
    """
    Queries the RescueGroups API for available pets based on specified criteria.

    Args:
        species (str): The species of the pet (e.g., "dog", "cat"). Defaults to None.
        age (str): The age group of the pet (e.g., "Baby", "Adult"). Defaults to None.

    Returns:
        list: A list of dictionaries containing information about the pets.
    """

    url = "https://api.rescuegroups.org/v5/public/animals/search/available/haspic"
    headers = {
        'Content-Type': 'application/vnd.api+json',
        'Authorization': RESCUEGROUPS_API_KEY
    }

    # Build the filter payload dynamically based on available parameters
    filters = []
    if species:
        filters.append({"fieldName": "species.singular", "operation": "equals", "criteria": species})
    if age:
        filters.append({"fieldName": "animals.ageGroup", "operation": "equals", "criteria": age})

    # Generate the `filterProcessing` string based on the number of filters
    filter_processing = " AND ".join(str(i + 1) for i in range(len(filters)))

    payload = {
        "data": {
            "filters": filters,
            "filterProcessing": filter_processing
        }
    }

    # Debugging: Log the payload
    print("Payload for API:", payload)

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

        # Extract pet details from the API response
        pets = []
        for animal in data.get('data', []):
            attributes = animal.get('attributes', {})
            pets.append({
                'name': attributes.get('name', 'Unknown name'),
                'breed': attributes.get('breedPrimary', 'Unknown breed'),
                'age': attributes.get('ageGroup', 'Unknown age'),
                'gender': attributes.get('sex', 'Unknown gender'),
                'location': attributes.get('foundPostalCode', 'Unknown location'),
                'image_url': attributes.get('pictureThumbnailUrl', 'No image available'),
                'pet_id': animal.get('id', 'Unknown ID')
            })
        return pets

    except requests.RequestException as e:
        print(f"Error querying the API: {e}")
        return []

@app.route('/pet/<pet_id>')
def profile(pet_id):
    # Fetch pet details from the API through pet_id
    pet = query_pet_by_id(pet_id)

    if not pet:
        abort(404, description="Pet not found.")

    return render_template('profile.html', pet=pet)

def clean_description(description):
    """
    Cleans and reformats the pet description text.
    - Decodes HTML entities like &nbsp;.
    - Adds logical paragraph breaks for readability.
    """
    if not description:
        return "No description available."

    # Decode HTML entities
    description = html.unescape(description)

    # Add paragraph breaks for logical separation (you can adjust these rules as needed)
    description = description.replace("UPDATE:", "\n\nUPDATE:")
    description = description.replace("Click here to", "\n\nClick here to")
    description = description.replace("Original post:", "\n\nOriginal post:")
    description = description.replace("&nbsp;", " ")

    # Remove extra spaces and ensure proper formatting
    description = " ".join(description.split())  # Remove excess whitespace
    description = description.strip()  # Trim leading and trailing whitespace

    return description

def query_pet_by_id(pet_id):
    # Fetch pet details from the API using the pet_id
    url = f"https://api.rescuegroups.org/v5/public/animals/{pet_id}"
    headers = {
        'Content-Type': 'application/vnd.api+json',
        'Authorization': RESCUEGROUPS_API_KEY
    }

    try:
        # Make a GET request to the API
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
        
        relationships = pet_data.get('relationships', {})

        # Create a mapping for location IDs to city names
        location_mapping = {}
        for included_item in data.get('included', []):
            if included_item['type'] == 'locations':
                location_id = included_item['id']
                city = included_item.get('attributes', {}).get('city', 'Unknown city')
                location_mapping[location_id] = city

        # Get the city from the location mapping        # Extract the location ID from relationships
        location_data = relationships.get('locations', {}).get('data', [])
        location_id = location_data[0]['id'] if location_data else None
        city = location_mapping.get(location_id, 'Unknown city')

        return {
            'name': attributes.get('name', 'Unknown name'),
            'breed': attributes.get('breedPrimary', 'Unknown breed'),
            'age': attributes.get('ageGroup', 'Unknown age'),
            'gender': attributes.get('sex', 'Unknown gender'),
            'description': clean_description(attributes.get('descriptionText', 'Unknown description')),
            'pet_id': pet_data.get('id', 'Unknown ID'),
            'image_url': attributes.get('pictureThumbnailUrl', 'No image available'),
            'city': city,
            'vaccinations': attributes.get('isCurrentVaccinations', 'Unknown vaccinations'),
        }

    except requests.RequestException as e:
        print(f"Error querying the API: {e}")
        return None

def generate_filter_string(x):
  # Generate a filter string for the API
  filter_string = ""
  for i in range(1, x + 1):
    filter_string += str(i)
    if i < x:
      filter_string += " AND "
  return filter_string

def query_pets_from_api(size, pet_type, shedding, age, training, temperment, zipcode):
    # Fetch pets from the API matching the parameters

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
    if temperment:
        filters.append({"fieldName": "animals.energyLevel", "operation": "equal", "criteria": temperment})
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

        # Extract the location ID from relationships
        location_data = relationships.get('locations', {}).get('data', [])
        location_id = location_data[0]['id'] if location_data else None
        city = location_mapping.get(location_id, 'Unknown city')

        pets.append({
            'name': attributes.get('name', 'Unknown name'),
            'breed': attributes.get('breedPrimary', 'Unknown breed'),
            'age': attributes.get('ageGroup', 'Unknown age'),
            'gender': attributes.get('sex', 'Unknown gender'),
            'city': city,
            'description': clean_description(attributes.get('descriptionText', 'Unknown description')),
            'pet_id': animal.get('id', 'Unknown ID'),
            'image_url': attributes.get('pictureThumbnailUrl', 'No image available'),
            'url': attributes.get('url', 'No URL available')
        })

    return pets

if __name__ == "__main__":
    app.run(debug=True)
