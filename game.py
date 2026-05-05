import random

def number_guessing_game():
    """Simple number guessing game"""
    number = random.randint(1, 100)
    attempts = 0
    guessed = False
    
    print("Welcome to the Number Guessing Game!")
    print("I'm thinking of a number between 1 and 100.")
    
    while not guessed:
        try:
            guess = int(input("Enter your guess: "))
            attempts += 1
            
            if guess < number:
                print("Too low! Try again.")
            elif guess > number:
                print("Too high! Try again.")
            else:
                guessed = True
                print(f"🎉 You guessed it! The number was {number}.")
                print(f"It took you {attempts} attempts.")
        except ValueError:
            print("Please enter a valid number.")

if __name__ == "__main__":
    number_guessing_game()
