:- discontiguous pet_match/2. % line to say its fine to define rules in different sections

% Pet Traits 

% Energy levels
pet_energy(dog, high).
pet_energy(cat, moderate).
pet_energy(rabbit, low).
pet_energy(bird, low).

% Grooming Needs
pet_grooming(dog, high).
pet_grooming(cat, low).
pet_grooming(rabbit, low).
pet_grooming(bird, low).

% Exercise Needs
pet_exercise(dog, high).
pet_exercise(cat, moderate).
pet_exercise(rabbit, moderate).
pet_exercise(bird, low).

% Vocals 
pet_vocal(dog, some).
pet_vocal(cat, quiet).
pet_vocal(bird, lots).
pet_vocal(rabbit, quiet).

% Shedding
pet_shedding(dog, moderate).
pet_shedding(cat, none).
pet_shedding(bird, none).
pet_shedding(rabbit, moderate).

% Training 
pet_training(dog, needs_training).
pet_training(cat, has_basic_training).
pet_training(bird, well_trained).
pet_training(rabbit, has_basic_training).

% Yard Needs 
pet_yard(dog).
pet_yard(cat).
pet_yard(rabbit).

% Favorite Pet 
pet_type(dog, dog).
pet_type(cat, cat).
pet_type(bird, bird).
pet_type(rabbit, rabbit).

% Size
pet_size(dog, medium).
pet_size(cat, medium).
pet_size(bird, small).
pet_size(rabbit, small).


% Rule 1 
pet_match(Adopter, Pet) :-
    adopter_energy(Adopter, Energy), pet_energy(Pet, Energy).

% Rule 2 
pet_match(Adopter, Pet) :- 
    adopter_exercise(Adopter, Exercise), pet_exercise(Pet, Exercise).

%  Rule 3 
pet_match(Adopter, Pet) :-
    adopter_training(Adopter, Training), pet_training(Pet, Training).

% Rule 4
pet_match(Adopter, Pet) :-
    adopter_yard(Adopter, _), pet_yard(Pet). 

% Rule 6 
pet_match(Adopter, Pet) :-
    adopter_grooming(Adopter, no_grooming), pet_grooming(Pet, low).

% Rule 7
pet_match(Adopter, Pet) :-
    adopter_grooming(Adopter, yes_grooming), pet_grooming(Pet, high).

% Rule 8
pet_match(Adopter, Pet) :-
    adopter_vocal(Adopter, Vocal), pet_vocal(Pet, Vocal).

% Rule 9
pet_match(Adopter, Pet) :-
    adopter_shedding(Adopter, Shedding), pet_shedding(Pet, Shedding).

% Rule 10
favorite_pet(AdopterChoice, Pet) :-
    pet_type(Pet, AdopterChoice).


% Rule 11 
pet_match(Adopter, Pet) :-
    adopter_kids(Adopter, yes), pet_size(Pet, medium).

% Rule 12
pet_match(Adopter, Pet) :-
    adopter_seniors(Adopter, yes), pet_size(Pet, small).





