from pyswip import Prolog

# Initialize Prolog
prolog = Prolog()
prolog.consult("pet_traits.pl")  # Load the Prolog file

# Function to test the main pet suggestion
def test_pet_suggestion(energy, allergies, living, children_status, preference_animal, yard, preference_age, pet_experience, train_preference):

    
    # Translate inputs
    allergy_value = "allergies" if allergies.lower() == "yes" else "no_allergies"
    
    # Query Prolog for matching pets based on user preferences
    query = f"""
        user_pet(Pet, {allergy_value}, {children_status}, {preference_animal}, {living}, {yard}, {preference_age}, {pet_experience}, {train_preference}, {energy}),
        pet(Pet, Temperament, Shedding, Size, Age, Training),
        PetFact = pet(Pet, Temperament, Shedding, Size, Age, Training)
    """

    results = list(prolog.query(query))
    if results:
        for result in results:
            # If using the structured term:
            # print(result["PetFact"])  # Will print something like pet(cat1, calm, no_shed, small, baby, trained)
            
            # Or if printing attributes individually:
            print(f"pet({result['Pet']}, {result['Temperament']}, {result['Shedding']}, {result['Size']}, {result['Age']}, {result['Training']}).")
    else:
        print("Sorry, no pets match your preferences.")



# Test cases
def main():
    print("Testing pet suggestions:")
    
    #Test case 1: Preference for dogs, no allergies, no children
    print("Test 1:", test_pet_suggestion("high_energy", "no", "house", "no_children", "dog", "yes", "baby", "beginner", "willing"))
    
    #Test case 2: Preference for cats, allergies, small children
    print("Test 2:", test_pet_suggestion("neutral", "no", "house", "no_children", "dog", "yes", "youth", "experienced", "willing"))
    
    #Test case 3: No preference, allergies, no children
    print("Test 3:", test_pet_suggestion("calm", "yes", "house", "no_children", "no_preference", "yes", "senior", "experienced", "willing"))

    print("Test 4:", test_pet_suggestion("calm", "no", "apartment", "no_children", "cat", "yes", "baby", "beginner", "not_willing"))

    print("Test 5:", test_pet_suggestion("neutral", "yes", "apartment", "small_children", "cat", "no", "youth", "experienced", "willing"))
    #["cat13", "cat15", "cat17", "cat37", "cat39", "cat41"] calm or neutral-energy cats suitable for small spaces, small children, and allergy-friendly

    print("Test 6:", test_pet_suggestion("high_energy", "no", "house", "small_children", "dog", "yes", "youth", "experienced", "willing"))
    #["dog9", "dog57"] large, high-energy, trained dogs that are family-friendly and meet the youth preference.

    print("Test 7:", test_pet_suggestion("calm", "yes", "house", "small_children", "no_preference", "yes", "senior", "beginner", "not_willing"))
    #["cat5", "dog5"] Allergy-friendly, calm, senior, trained pets (dogs or cats) suitable for small children.

    print("Test 8:", test_pet_suggestion("calm", "no", "apartment", "no_children", "cat", "no", "baby", "beginner", "willing"))
    #["cat1", "cat13", "cat37"] Calm, small, baby cats suitable for apartments and beginner pet owners.

    print("Test 9:", test_pet_suggestion("high_energy", "yes", "house", "no_children", "dog", "no", "youth", "experienced", "willing"))
    #["dog3", "dog27"] High-energy, allergy-friendly, small, trained dogs suitable for a house without a yard.

    print("Test 10:", test_pet_suggestion("neutral", "no", "apartment", "no_children", "no_preference", "no", "baby", "beginner", "willing"))
    #["cat1", "dog1"] Calm or neutral-energy, small, baby pets (dogs or cats) suitable for apartments and beginner owners.



if __name__ == "__main__":
    main()
