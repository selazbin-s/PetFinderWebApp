% Facts about cats
pet(cat1, calm, no_shed, apartment, small).
pet(cat2, calm, no_shed, apartment, large).
pet(cat3, calm, no_shed, house, small).
pet(cat4, calm, no_shed, house, large).
pet(cat5, calm, shed, apartment, small).
pet(cat6, calm, shed, apartment, large).
pet(cat7, calm, shed, house, small).
pet(cat8, calm, shed, house, large).

pet(cat9, neutral, no_shed, apartment, small).
pet(cat10, neutral, no_shed, apartment, large).
pet(cat11, neutral, no_shed, house, small).
pet(cat12, neutral, no_shed, house, large).
pet(cat13, neutral, shed, apartment, small).
pet(cat14, neutral, shed, apartment, large).
pet(cat15, neutral, shed, house, small).
pet(cat16, neutral, shed, house, large).

pet(cat17, high_energy, no_shed, apartment, small).
pet(cat18, high_energy, no_shed, apartment, large).
pet(cat19, high_energy, no_shed, house, small).
pet(cat20, high_energy, no_shed, house, large).
pet(cat21, high_energy, shed, apartment, small).
pet(cat22, high_energy, shed, apartment, large).
pet(cat23, high_energy, shed, house, small).
pet(cat24, high_energy, shed, house, large).

% Facts about dogs
pet(dog1, calm, no_shed, apartment, small).
pet(dog2, calm, no_shed, apartment, large).
pet(dog3, calm, no_shed, house, small).
pet(dog4, calm, no_shed, house, large).
pet(dog5, calm, shed, apartment, small).
pet(dog6, calm, shed, apartment, large).
pet(dog7, calm, shed, house, small).
pet(dog8, calm, shed, house, large).

pet(dog9, neutral, no_shed, apartment, small).
pet(dog10, neutral, no_shed, apartment, large).
pet(dog11, neutral, no_shed, house, small).
pet(dog12, neutral, no_shed, house, large).
pet(dog13, neutral, shed, apartment, small).
pet(dog14, neutral, shed, apartment, large).
pet(dog15, neutral, shed, house, small).
pet(dog16, neutral, shed, house, large).

pet(dog17, high_energy, no_shed, apartment, small).
pet(dog18, high_energy, no_shed, apartment, large).
pet(dog19, high_energy, no_shed, house, small).
pet(dog20, high_energy, no_shed, house, large).
pet(dog21, high_energy, shed, apartment, small).
pet(dog22, high_energy, shed, apartment, large).
pet(dog23, high_energy, shed, house, small).
pet(dog24, high_energy, shed, house, large).

% Derived rules
small_pet(Pet) :- pet(Pet, _, _, _, small).
large_pet(Pet) :- pet(Pet, _, _, _, large).
low_energy_pet(Pet) :- pet(Pet, calm, _, _, _).
high_energy_pet(Pet) :- pet(Pet, high_energy, _, _, _).
allergy_friendly_pet(Pet) :- pet(Pet, _, no_shed, _, _).

% Rule: Ensure allergy-friendly pets are labeled as no_shed
allergy_friendly_pet(Pet) :- pet(Pet, _, no_shed, _, _).

% Rule: Disallow large pets in apartments
valid_pet(Pet) :-
    pet(Pet, _, _, apartment, small).  % Allow small pets in apartments
valid_pet(Pet) :-
    pet(Pet, _, _, house, _).         % Allow all pets in houses

% Rule: Disallow large high-energy pets for families with small children
family_friendly_pet(Pet, no_children) :- 
    valid_pet(Pet).  % If no small children, defer to valid_pet/1
family_friendly_pet(Pet, small_children) :- 
    valid_pet(Pet),  % Must be valid first
    \+ (pet(Pet, high_energy, _, _, large)).  % Exclude large high-energy pets

% Rule: Ensure pets are valid and allergy-friendly if user has allergies
user_pet(Pet, no_allergies, no_children, no_preference) :-
    valid_pet(Pet), family_friendly_pet(Pet, no_children).
user_pet(Pet, no_allergies, small_children, no_preference) :-
    valid_pet(Pet), family_friendly_pet(Pet, small_children).
user_pet(Pet, allergies, no_children, no_preference) :-
    valid_pet(Pet), family_friendly_pet(Pet, no_children), allergy_friendly_pet(Pet).
user_pet(Pet, allergies, small_children, no_preference) :-
    valid_pet(Pet), family_friendly_pet(Pet, small_children), allergy_friendly_pet(Pet).

% Rule: Handle user preferences for dogs, cats, or no preference
user_pet(Pet, Allergies, Children, dog_preference) :-
    valid_pet(Pet), family_friendly_pet(Pet, Children), pet(Pet, _, _, _, _), sub_atom(Pet, 0, _, _, dog), allergy_friendly_check(Allergies, Pet).
user_pet(Pet, Allergies, Children, cat_preference) :-
    valid_pet(Pet), family_friendly_pet(Pet, Children), pet(Pet, _, _, _, _), sub_atom(Pet, 0, _, _, cat), allergy_friendly_check(Allergies, Pet).
user_pet(Pet, Allergies, Children, no_preference) :-
    user_pet(Pet, Allergies, Children, dog_preference); user_pet(Pet, Allergies, Children, cat_preference).

% Rule: Helper to check allergy constraints
allergy_friendly_check(allergies, Pet) :-
    allergy_friendly_pet(Pet).
allergy_friendly_check(no_allergies, _).
