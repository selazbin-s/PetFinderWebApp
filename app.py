from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)
app.app_context().push()

# Example Questions for the Quiz
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
        # Get the selected option
        selected_option = request.form['option']
        print(f"Answer to Question {question_id}: {selected_option}")
        # Get the next question
        return redirect(url_for('quiz', question_id=question_id + 1))
    
    return render_template('quiz.html', question=current_question, total=len(QUESTIONS))

@app.route('/results')
def results():
    return render_template('results.html')

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

# Will Implement later when we have dataset avaiable
# @app.route('/pet/<int:pet_id>')
# def pet_profile(pet_id):
#     # Placeholder: fetch pet details from database
#     pet = {'id': pet_id, 'name': 'Max', 'species': 'Dog', 'breed': 'Labrador', 'age': 'Puppy'}
#     return render_template('pet_profile.html', pet=pet)

@app.route('/pet')
def profile():
    return render_template('profile.html')

if __name__ == "__main__":
    app.run(debug=True)
