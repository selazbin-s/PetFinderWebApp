from pyswip import Prolog


prolog = Prolog()
prolog.consult("C:/Users/happy/Desktop/PetFinderWebApp/Prolog/pet_traits.pl")

def query_pet_match(adopter_traits):
    # Map dictionary keys
    trait_mapping = {
        "energy": "adopter_energy",
        "exercise": "adopter_exercise",
        "training": "adopter_training",
        "yard": "adopter_yard",
        "grooming": "adopter_grooming",
        "vocal": "adopter_vocal",
        "shedding": "adopter_shedding",
        "kids": "adopter_kids",
        "seniors": "adopter_seniors"
    }


    # Dynamically assert traits into the Prolog database
    for key, value in adopter_traits.items():
        if key in trait_mapping:
            prolog.assertz(f"{trait_mapping[key]}(adopter, {value})")  # Dynamically insert facts


    results = prolog.query("pet_match(adopter, Pet)")
   
    matched_pets = []
    for result in results:
        matched_pets.append(result["Pet"])


    return matched_pets


# Dynamically collect user traits
adopter_traits = {}
adopter_traits['energy'] = input("Enter energy level (high/moderate/low): ")
adopter_traits['exercise'] = input("Enter exercise needs (high/moderate/low/not required): ")
adopter_traits['training'] = input("Enter training level (needs_training/has_basic_training/well_trained): ")
adopter_traits['yard'] = input("Do you have a yard? (yes/no): ")
adopter_traits['grooming'] = input("Are you okay taking the pet for grooming? (yes_grooming/no_grooming): ")
adopter_traits['vocal'] = input("What is your preferred vocal level for the pet? (quiet/some/lots): ")
adopter_traits['shedding'] = input("How much shedding are you okay with? (none/moderate/high): ")
adopter_traits['kids'] = input("Do you have or expect kids? (yes/no): ")
adopter_traits['seniors'] = input("Do you senior people living with you? (yes/no): ")


# Call the function to query the best pet match
pet_match = query_pet_match(adopter_traits)
print(f"Best matched pets: {pet_match}")
