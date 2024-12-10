from pyswip import Prolog

# Initialize Prolog
prolog = Prolog()
prolog.consult("pet_traits.pl")  # Load the Prolog file

# Function to test the main pet suggestion
def test_pet_suggestion(energy, allergies, living, size, small_children, preference):
    # Translate inputs
    allergy_value = "allergies" if allergies.lower() == "yes" else "no_allergies"
    children_status = "small_children" if small_children else "no_children"
    
    # Query Prolog for matching pets based on user preferences
    query = f"user_pet(Pet, {allergy_value}, {children_status}, {preference}), pet(Pet, {energy}, _, {living}, {size})"
    results = list(prolog.query(query))
    
    # Return results or a failure message
    if results:
        return [result["Pet"] for result in results]
    else:
        return "Sorry, no pets match your preferences."

# Test cases
def main():
    print("Testing pet suggestions:")
    
    # Test case 1: Preference for dogs, no allergies, no children
    print("Test 1:", test_pet_suggestion("high_energy", "no", "house", "large", False, "dog_preference"))
    
    # Test case 2: Preference for cats, allergies, small children
    print("Test 2:", test_pet_suggestion("neutral", "yes", "apartment", "small", True, "cat_preference"))
    
    # Test case 3: No preference, allergies, no children
    print("Test 3:", test_pet_suggestion("calm", "yes", "house", "large", False, "no_preference"))

if __name__ == "__main__":
    main()
