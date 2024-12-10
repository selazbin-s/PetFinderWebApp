% Rule 1 - more exercise + energy

pet_match(Adopter, dog) :-
    adopter_energy(Adopter, high), adopter_exercise(Adopter, high).

% Rule 2 - low energy + grooming
pet_match(Adopter, cat) :-
    adopter_energy(Adopter, low), adopter_grooming(Adopter, low).

% Rule 3 - more exercise + medium size 
pet_match(Adopter, dog) :-
    adopter_exercise(Adopter, high), adopter_size(Adopter, medium).

% Rule 4 - low exercise + medium size 
pet_match(Adopter, cat) :-
    adopter_exercise(Adopter, moderate), adopter_size(Adopter, medium).

% Rule 5 - Seniors with cats + low energy
pet_match(Adopter, cat) :-
    adopter_age(Adopter, senior), adopter_energy(Adopter, low).

% Rule 6 - low energy + exercise 
pet_match(Adopter, cat) :-
    adopter_energy(Adopter, low), adopter_exercise(Adopter, low).

% Rule 7 -good training 
pet_match(Adopter, dog) :-
    adopter_training(Adopter, has_basic_training).

% Rule 8 - Has yard 
pet_match(Adopter, dog) :-
    adopter_yard(Adopter).

% Rule 9 - low grooming + shedding 
pet_match(Adopter, cat) :-
    adopter_grooming(Adopter, low), adopter_length(Adopter, short).


% Rule 10 - high grooming + shedding 
pet_match(Adopter, dog) :-
    adopter_grooming(Adopter, high), adopter_length(Adopter, medium).

% Rule 11 - Seniors with dogs + high energy
pet_match(Adopter, dog) :-
    adopter_kid(Adopter, kids), adopter_energy(Adopter, high).

% Rule 12 - Favorite choice
pet_match(Adopter, dog) :-
    adopter_favorite(Adopter, dog).
pet_match(Adopter, cat) :-
    adopter_favorite(Adopter, cat).


% Rule 13 - high exercise + likes dogs 
pet_match(adopter, dog) :-
    adopter_exercise(adopter, high), isDogsOk(adopter).

% Rule 14 - low exercise + likes cats
pet_match(adopter, cat) :-
    adopter_exercise(adopter, low), isCatsOk(adopter).

% Rule 15 - small size + no yard
pet_match(Adopter, cat) :-
    adopter_size(Adopter, small), not(adopter_yard(Adopter)).

% Rule 16 - high vocal
pet_match(Adopter, dog) :-
    adopter_vocalLevel(Adopter, lots).


% Rule 15 - Choose other if some other choices 
pet_match(Adopter, other) :-
    not(isDogsOk(Adopter)), not(iscatsOk(Adopter)).






