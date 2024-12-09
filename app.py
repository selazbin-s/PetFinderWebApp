from flask import Flask, render_template, url_for, request, redirect, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from pyswip import Prolog
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.secret_key = "supersecretkey"  # For session usage
db = SQLAlchemy(app)
app.app_context().push()

RESCUEGROUPS_API_KEY = "SP1Mg1Jg"

# Initialize Prolog
prolog = Prolog()
# Example Prolog rules (you can adjust these based on your logic)
prolog.assertz("small_pet(cat)")
prolog.assertz("small_pet(rabbit)")
prolog.assertz("large_pet(dog)")
prolog.assertz("large_pet(horse)")
prolog.assertz("suitable_pet(X, small) :- small_pet(X)")
prolog.assertz("suitable_pet(X, large) :- large_pet(X)")
prolog.assertz("pet_suggestion(true, X) :- suitable_pet(X, small)")
prolog.assertz("pet_suggestion(false, X) :- suitable_pet(X, large)")

# Example Questions for the Quiz
QUESTIONS = [
    {'id': 1, 'question': 'Do you have small children?',
     'options': [
        {'id': 1, 'option': 'Yes'},
        {'id': 2, 'option': 'No'}
    ]},
    {'id': 2, 'question': 'Where do you live?', 
     'options': [
        {'id': 1, 'option': 'Apartment'},
        {'id': 2, 'option': 'House with Yard'},
        {'id': 3, 'option': 'House without Yard'},
        {'id': 4, 'option': 'Other'},
    ]},
    {'id': 3, 'question': 'What is your current Zip Code?',
     'options': []  # No predefined options; user will type input
    },
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
    answers = session.get('answers', {})
    has_children_i = answers.get('q1')
    if has_children_i=='yes':
        has_children=True
    else:
        has_children=False
    living = answers.get('q2', 'other')
    zipcode = answers.get('q3')  # Default if none provided
    print("zipcode Answers:", answers.get('q3'))

    # Assert facts into Prolog
    result = list(prolog.query(f"pet_suggestion({str(has_children).lower()}, X)"))


    # Query Prolog
    #results_list = list(prolog.query("suitable_pet(X)"))
    pet_type_i = result[0]['X'] if result else "none"

    # pets = query_pets_from_api(exerciseNeeds, isYardRequired, zipcode)
    print(f"Pet type_i:  {pet_type_i}")

    if pet_type_i=='dog':
        pet_type='Large'
    else:
        pet_type='Small'
    pets = query_pets_from_api(pet_type,zipcode)
    
    first_pet = pets[0] if pets else None
 
    return render_template('results.html', recommended_pet=pet_type, pets=pets, first_pet=first_pet)

@app.route('/browse', methods=['GET'])
def browse():
    # Example data
    species_list = ['Dog', 'Cat', 'Rabbit']
    breed_list = ['Labrador', 'Siamese', 'Rex']
    age_list = ['Puppy', 'Kitten', 'Adult']
    
    # Capture filter parameters
    selected_species = request.args.get('species')
    selected_breed = request.args.get('breed')
    selected_age = request.args.get('age')
    
    # Placeholder: filter logic (e.g., querying database)
    filtered_pets = []  # Example: apply filters to fetch pets
    
    return render_template('browse.html', 
                           species_list=species_list,
                           breed_list=breed_list,
                           age_list=age_list,
                           pets=filtered_pets)

@app.route('/pet')
def profile():
    return render_template('profile.html')

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
            'image_url': attributes.get('pictureThumbnailUrl', 'No image available'),
            'url': attributes.get('url', 'No URL available')
        })

    return pets

if __name__ == "__main__":
    app.run(debug=True)
