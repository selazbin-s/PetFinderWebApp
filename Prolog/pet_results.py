from pyswip import Prolog


prolog = Prolog()
prolog.consult("C:/Users/happy/Desktop/PetFinderWebApp/Prolog/pet_traits.pl")


# Function to map user responses to Prolog facts dynamically
def assert_traits(user_responses):
    for key, value in user_responses.items():
        # Dynamically assert user response into the Prolog database
        prolog.assertz(f"{key}(adopter, {value})")


# Example: Collect responses from the user
def ask_questions():
    print("Answer the following questions to find your ideal pet!")
    
    # Ask situational/behavioral questions and map the answers
    energy_response = input("How much time do you spend exercising each week? (high/moderate/low): ")
    exercise_response = input("Do you enjoy working out? (yes/no): ")
    allergies_response = input("Do you have allergies? (yes/no): ")
    yard_response = input("Do you have a yard? (yes/no): ")
    noise_tolerance = input("Do you like environments with quiteness or lots of noise? (quiet/moderate/lots): ")
    senior_response = input("Do you have elderly people in the house? (yes/no): ")
    training_response = input("Do you stay home a lot or not? (yes/no): ")
    
    # Map responses to Prolog traits
    user_responses = {
        "adopter_energy": energy_response,
        "adopter_exercise": exercise_response,
        "adopter_allergies": allergies_response,
        "adopter_yard": yard_response,
        "adopter_vocalLevel": noise_tolerance,
        "adopter_age": senior_response,
        "adopter_training": training_response,
        
    }

    # Dynamically assert these traits into Prolog
    assert_traits(user_responses)


# Query Prolog to determine ideal pet match
def query_pet_match():
    results = prolog.query("pet_match(adopter, Pet)")
    matched_pets = []
    for result in results:
        matched_pets.append(result["Pet"])
    return matched_pets


def main():
    ask_questions()
    
    result = query_pet_match()
    
    print("The pet you should adopt is: ", result)


if __name__ == "__main__":
    main()



