from pyswip import Prolog

# Initialize Prolog
prolog = Prolog()
prolog.consult("pet_traits.pl")  # Load the Prolog file

# Function to test the main pet suggestion
def test_pet_suggestion(energy, allergies, living, size, small_children, preference_animal, yard, preference_age, pet_experience, train_preference):
    # Translate inputs
    allergy_value = "allergies" if allergies.lower() == "yes" else "no_allergies"
    children_status = "small_children" if small_children else "no_children"
    
    # Query Prolog for matching pets based on user preferences
    query = f"user_pet(Pet, {allergy_value}, {children_status}, {preference_animal}, {living}, {yard}, {preference_age}, {pet_experience}, {train_preference}), pet(Pet, {energy}, _, {size}, _, _)"
    results = list(prolog.query(query))
    
    # Remove duplicates
    unique_results = list({result["Pet"] for result in results})
    
    # Return results or a failure message
    if unique_results:
        return unique_results
    else:
        return "Sorry, no pets match your preferences."

# Test cases
def main():
    print("Testing pet suggestions:")
    
    # Test case 1: Preference for dogs, no allergies, no children
    print("Test 1:", test_pet_suggestion("high_energy", "no", "house", "large", False, "dog_preference", "yes", "baby", "beginner", "willing"))
    
    # Test case 2: Preference for cats, allergies, small children
    print("Test 2:", test_pet_suggestion("neutral", "no", "apartment", "small", False, "cat_preference", "yes", "young", "expereinced", "not_willing"))
    
    # Test case 3: No preference, allergies, no children
    print("Test 3:", test_pet_suggestion("calm", "yes", "house", "large", False, "no_preference", "yes", "senior", "experienced", "willing"))

    print("Test 4:", test_pet_suggestion("calm", "no", "apartment", "small", False, "cat_preference", "yes", "baby", "beginner", "not_willing"))

if __name__ == "__main__":
    main()
