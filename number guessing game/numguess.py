import random

def game_rules():
    print("="*30)
    print("Welcome to the Number Guessing Game!")
    print("="*30)
    print("I am thinking of a number between 1 and 100.")
    print("You have a number of attempts to guess the number based on difficulty .")
    print("Good luck!")

def difficulty_guess():
    while True:
        level = input("Choose a difficulty: 'easy' or 'medium' or 'hard'- ").lower()
        #try:
        if level == "easy":
            print("You have 10 attempts to guess the correct number.")
            return 10
        elif level == "medium":
            print("You have 6 attempts to guess the correct number.")
            return 6
        elif level == "hard":
            print("You have 4 attempts to guess the correct number.")
            return 4
        else:
            print("Invalid input. Please enter 'easy', 'medium', or 'hard'.")
            #print("You have 4 attempts to guess the correct number.")
            #return 4
        #except ValueError:
            #print("Invalid input. Please enter 'easy', 'medium', or 'hard'.")
            #return difficulty_guess()
    
def guess_number():
    number = random.randint(1, 100)
    return number

def check_guess(number, guess):
    #guess = int(input("Enter you guess: "))
    try:
        if guess == number:
            print(f"You got it! The number is {number}")
            print("Congratulations! You win. ")
            return True
        elif guess > number:
            print("Guess is too high. Try again. ")
            return False
        elif guess < number:
            print("Guess is too low. Try again.")
            return False
        #else:
            #print("Invalid input. Please enter a number between 1 and 100.")
            #return False
    except ValueError:
        print("Invalid input. Please enter a number.")
        return False
    
'''def num_of_guesses():
    num_of_guesses = 0
    difficulty = difficulty_guess()
    while num_of_guesses < difficulty:
        if check_guess(number):
            break
        num_of_guesses += 1
    print(f"You guessed the number in {num_of_guesses} attempts.")
    '''

def main():
    game_rules()
    number = guess_number()
    attempts_used = 0
    attempts_rem = difficulty_guess()

    while attempts_rem > 0:
        print(f"\n You have {attempts_rem} attempts left.")

        try:
            guess = int(input("Enter your guess: "))
            if guess < 1 or guess > 100:
                print("Please enter a number between 1 and 100.")
                continue
        except ValueError:
            print("Invalid input.Please enter a number.")
            continue

        attempts_used += 1
        attempts_rem -= 1

        if guess == number:
            print(f"You got it! The number is {number}")
            print("Congratulations! You win. ")
            print(f"You guessed the number in {attempts_used} attempts.")
            return
        elif guess > number:
            print("Guess is too high. Try again.")
        elif guess < number:
            print("Guess is too low. Try again.")

    print(f"\nGame over! You've run out of attempts.")
    print(f"The number was {number}.")

if __name__ == "__main__":
    main()    

    






