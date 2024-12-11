from flask import Flask, render_template, url_for, request, redirect, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from pyswip import Prolog
import requests
from bs4 import BeautifulSoup
import subprocess

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.secret_key = "supersecretkey"  # For session usage
db = SQLAlchemy(app)
app.app_context().push()

RESCUEGROUPS_API_KEY = "SP1Mg1Jg"

# Initialize Prolog
prolog = Prolog()
prolog.consult("pet_traits.pl")  # Load the Prolog file

# Example Questions for the Quiz
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
        {'id': 2, 'option': 'Youth'},
        {'id': 3, 'option': 'Senior'},
        {'id': 4, 'option': 'No preference'},
    ]},      
    {'id': 7, 'question': 'Have you cared for a pet before', 
     'options': [
        {'id': 1, 'option': 'Yes'},
        {'id': 2, 'option': 'No'},
    ]}, 
    {'id': 8, 'question': 'Are you willing to train a new animal?', 
     'options': [
        {'id': 1, 'option': 'Yes'},
        {'id': 2, 'option': 'No'},
    ]},             
    # {'id': 3, 'question': 'What is your current Zip Code?',
    #  'options': []  # No predefined options; user will type input
    # },
]

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Task %r>' % self.id

@app.route('/', methods=['POST', 'GET'])
def index():
    session.clear() 
    if request.method == 'POST':
        task_content = request.form['content']
        new_task = Todo(content=task_content)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding your task'

    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
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



        # Debugging session after update

        print("Session after update:", session.get('answers'))

        return redirect(url_for('quiz', question_id=question_id + 1))

    return render_template('quiz.html', question=current_question, total=len(QUESTIONS))



@app.route('/results')
def results():

    ###formatting input answers for API
    answers = session.get('answers', {})
    energy = answers.get('q1')
    if energy=="high energy":
        energy="high_energy"
    elif energy=="calm":
        energy="calm"
    else:
        energy="neutral"
    
    allergies = answers.get('q2')
    if allergies == "Yes":
        allergy_value = "allergies"
    else:
        allergy_value="no_allergies"

    living = answers.get('q3')
    living=living.split()[0]
    if living=="House with a Yard":
        yard="yes"
    else:
        yard="no"

    small_children = answers.get('q4')
    if small_children == "yes":
        children_status = "small_children"
    else:
        children_status = "no_children"

    preference_animal = answers.get('q5')
    if preference_animal=="no preference":
        preference_animal="no_preference"

    preference_age = answers.get('q6')
    if preference_age=="no preference":
        preference_age="no_preference"

    pet_experience = answers.get('q7')
    if pet_experience=="Yes":
        pet_experience="experienced"
    else:
        pet_experience="beginner"
    
    train_preference = answers.get('q8')
    if train_preference=="no":
        train_preference="not_willing"
    else:
        train_preference="willing"

    # Query Prolog for matching pets based on user preferences
    query = (
    f"user_pet(Pet, {allergy_value}, {children_status}, {preference_animal}, {living}, {yard}, {preference_age}, {pet_experience}, {train_preference}, {energy})"
    )

    result = subprocess.run(
        ["swipl", "-q", "-s", "pet_traits.pl", "-g", query, "-t", "halt"],
        stdout=subprocess.PIPE,
        text=True
    )

    # Capture the output from `write/1`
    explanation = result.stdout.strip()

    results = list(prolog.query(query))
    
    # Remove duplicates
    unique_results = list({result["Pet"] for result in results})
    
    # Return results or a failure message
    if unique_results:
        for x in unique_results:
            print(x)
    else:
        return "Sorry, no pets match your preferences."
    
    
    pet_type='Small'
    pets = query_pets_from_api(pet_type,'92701')
    
    first_pet = pets[0] if pets else None
 
    return render_template('results.html', recommended_pet=first_pet, pets=pets, first_pet=first_pet, explanation=explanation, results=results)

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
            'gender': attributes.get('gender', 'Unknown gender'),
            'description': description,
            'pet_id': pet_data.get('id', 'Unknown ID'),
            'image_url': attributes.get('pictureThumbnailUrl', 'No image available'),
        }

    except requests.RequestException as e:
        print(f"Error querying the API: {e}")
        return None

def query_pets_from_api(pet_type, zipcode):
    url = "https://api.rescuegroups.org/v5/public/animals/search/available/haspic"
    headers = {
        'Content-Type': 'application/vnd.api+json',
        'Authorization': RESCUEGROUPS_API_KEY
    }

    # Minimal payload as per API requirements
    payload = {
    "data": {
        "filters": 
    	[
    		{
    			"fieldName": "animals.sizeGroup",
    			"operation": "equal",
    			"criteria": pet_type
    		}
    	],
    	"filterProcessing": "1",
        "filterRadius":
        	{
        		"miles": 100,
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
            'gender': attributes.get('gender', 'Unknown gender'),
            'city': city,
            'description': description,
            'pet_id': animal.get('id', 'Unknown ID'),
            'image_url': attributes.get('pictureThumbnailUrl', 'No image available'),
            'url': attributes.get('url', 'No URL available')
        })

    return pets

if __name__ == "__main__":
    app.run(debug=True)
