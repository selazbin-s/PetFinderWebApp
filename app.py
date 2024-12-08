from flask import Flask, render_template, url_for, request, redirect, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from pyswip import Prolog
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.secret_key = "supersecretkey"  # For session usage
db = SQLAlchemy(app)
app.app_context().push()

RESCUEGROUPS_API_KEY = "SP1Mg1Jg"

# Initialize Prolog
prolog = Prolog()
# Example Prolog rules (you can adjust these based on your logic)
prolog.assertz("suitable_pet(dog) :- favorite_pet(dog), has_yard(true)")
prolog.assertz("suitable_pet(cat) :- favorite_pet(cat), has_yard(false)")
prolog.assertz("suitable_pet(fish) :- favorite_pet(fish)")
prolog.assertz("suitable_pet(other) :- favorite_pet(other)")

# Example Questions for the Quiz
# 1: Favorite pet
# 2: Living situation
# 3: Zip Code
QUESTIONS = [
    {'id': 1, 'question': 'What is your favorite pet?',
     'options': [
        {'id': 1, 'option': 'Cat'},
        {'id': 2, 'option': 'Dog'},
        {'id': 3, 'option': 'Fish'},
        {'id': 4, 'option': 'Other'}
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
    if request.method == 'POST':
        task_content = request.form['content']
        new_task = Todo(content=task_content)
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect(url_for('index'))
        except:
            return 'There was an issue adding your task'
    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template('index.html', tasks=tasks)

@app.route('/quiz/<int:question_id>', methods=['GET', 'POST'])
def quiz(question_id):
    current_question = next((q for q in QUESTIONS if q['id'] == question_id), None)
    if not current_question:
        # No more questions, go to results
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

        # Store the answer in session
        if 'answers' not in session:
            session['answers'] = {}
        session['answers'][f'q{question_id}'] = selected_option_text.lower().strip()

        return redirect(url_for('quiz', question_id=question_id + 1))

    return render_template('quiz.html', question=current_question, total=len(QUESTIONS))

@app.route('/results')
def results():
    answers = session.get('answers', {})
    favorite = answers.get('q1', 'other')
    living = answers.get('q2', 'other')
    zipcode = answers.get('q3', '92701')  # Default if none provided

    # Assert facts into Prolog
    prolog.assertz(f"favorite_pet({favorite})")
    yard = 'true' if 'yard' in living else 'false'
    prolog.assertz(f"has_yard({yard})")

    # Query Prolog
    results_list = list(prolog.query("suitable_pet(X)"))
    pet_type = results_list[0]['X'] if results_list else "none"

    # Map pet_type to exerciseNeeds and isYardRequired for the API
    # Adjust logic as needed
    if pet_type == 'dog':
        exerciseNeeds = 'high'
        isYardRequired = 'true'
    elif pet_type == 'cat':
        exerciseNeeds = 'low'
        isYardRequired = 'false'
    elif pet_type == 'fish':
        exerciseNeeds = 'not_required'
        isYardRequired = 'false'
    else:
        exerciseNeeds = 'not_required'
        isYardRequired = 'false'

    # Query pets within 20 miles of the provided zip code
    # pets = query_pets_from_api(exerciseNeeds, isYardRequired, zipcode)
    pets = query_pets_from_api(zipcode)

    return render_template('results.html', recommended_pet=pet_type, pets=pets)

def query_pets_from_api(zipcode):
    url = "https://api.rescuegroups.org/v5/public/animals/search/available/haspic"
    headers = {
        'Content-Type': 'application/vnd.api+json',
        'Authorization': RESCUEGROUPS_API_KEY
    }

    # Minimal payload as per API requirements
    payload = {
        "data": {
            "filterRadius": {
                "miles": 10,
                "postalcode": str(zipcode)
            }
        }
    }

    try:
        # Log headers and payload for debugging
        print("Headers:", headers)
        print("Payload:", payload)

        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        print(f"Error querying the API: {e}")
        data = {'data': []}

    pets = []
    for animal in data.get('data', []):
        attributes = animal.get('attributes', {})
        pets.append({
            'name': attributes.get('name', 'Unknown name'),
            'breed': attributes.get('breedPrimary', 'Unknown breed'),
            'age': attributes.get('ageGroup', 'Unknown age'),
            'foundPostalcode': attributes.get('foundPostalcode', 'Unknown location'),
            'description': attributes.get('descriptionText', 'No description available')
        })

    return pets

if __name__ == "__main__":
    app.run(debug=True)
