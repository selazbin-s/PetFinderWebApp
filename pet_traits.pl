% pet(cat1, calm, no_shed, small, baby, trained).
:- dynamic pet/6.
pet(11111, calm, low, medium, adult, trained).

% Helper Predicates

% House Size Check
house_size(Pet, apartment) :- pet(Pet, _, _, small, _, _).  % Only small pets for apartments
house_size(Pet, house) :- pet(Pet, _, _, _, _, _).          % All pets for houses

% Family-friendliness
family_friendly_pet(_, no_children).  % All pets are suitable for families without children
family_friendly_pet(Pet, small_children) :-
    \+ (pet(Pet, high_energy, _, large, _, no_trained)).  % Exclude large, high-energy, untrained pets

% Check allergy constraints
allergy_check(allergies, Pet) :- pet(Pet, _, no_shed, _, _, _).  % Allow only allergy-friendly pets
allergy_check(no_allergies, _).  % Allow all pets if no allergies

% Check preference for animal
preference_animal(_, no_preference).
preference_animal(Pet, dog) :- atom_prefix(Pet, dog).
preference_animal(Pet, cat) :- atom_prefix(Pet, cat).

% If no yard then no high-energy dogs
yard_check(_, yes).  % If the user has a yard, all pets are allowed
yard_check(Pet, no) :-
    \+ (pet(Pet, high_energy, _, _, _, no_trained), sub_atom(Pet, 0, _, _, dog)).  % Exclude untrained, high-energy dogs if no yard

% Check preference for age
preference_age(_, no_preference).  % No preference for age
preference_age(Pet, Age) :- pet(Pet, _, _, _, Age, _).  % Match specific age preference

% No two babies at the same time
children_baby(_, no_children).  % No restriction if there are no children
children_baby(Pet, small_children) :- 
    \+ (pet(Pet, _, _, _, baby, no_trained)).  % Exclude baby animals if they are untrained and there are small children

% Beginner pet
beginner_pet(Pet, beginner) :- 
    (pet(Pet, _, _, small, _, trained), sub_atom(Pet, 0, _, _, cat));  % Small, trained cats
    (pet(Pet, _, _, _, _, trained), sub_atom(Pet, 0, _, _, dog)).     % Any size, trained dogs
beginner_pet(_, experienced).  % No restriction for experienced pet owners

% Rule to ensure only trained pets are selected if the user does not want to train an animal
training_preference(_, willing).  % If the user is willing to train, no restriction
training_preference(Pet, not_willing) :-
    \+ pet(Pet, _, _, _, _, no_trained).  % Exclude untrained pets if the user does not want to train

% Energy level preference rule
preference_energy(Pet, Energy) :-
    pet(Pet, Energy, _, _, _, _).

% Matches users with their perfect match
user_pet(Pet, Allergies, Children, Preference, Living, Yard, Age, Experience, Training, Energy) :-
   house_size(Pet, Living),  % Match the pets size to the living environment
   family_friendly_pet(Pet, Children),  % Ensure family-friendliness
   children_baby(Pet, Children),  % Ensure age is safe children
   allergy_check(Allergies, Pet),  % Check allergy constraints
   preference_animal(Pet, Preference),  % Match species preference
   yard_check(Pet, Yard),  % Ensure suitability based on yard availability
   preference_age(Pet, Age),  % Match the pets age preference
   beginner_pet(Pet, Experience),  % Match beginner pet owner preferences
   training_preference(Pet, Training),  % Ensure the pet matches the users training willingness
   preference_energy(Pet, Energy),
   % Write explanation to the output
   write("This pet is a great match because it meets the following criteria:\n"),
   format("Pet: ~w\n", [Pet]),
   format("Allergies: ~w\n", [Allergies]),
   format("Children: ~w\n", [Children]),
   format("Preference: ~w\n", [Preference]),
   format("Living: ~w\n", [Living]),
   format("Yard: ~w\n", [Yard]),
   format("Age: ~w\n", [Age]),
   format("Experience: ~w\n" , [Experience]),
   format("Training Needed: ~w\n", [Training]),
   format("Energy: ~w\n", [Energy]).

