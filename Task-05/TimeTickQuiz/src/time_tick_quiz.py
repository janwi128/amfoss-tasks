import requests
import json
import threading
import time

def get_question(): 
    url = "https://opentdb.com/api.php?amount=1&type=multiple"
    response = requests.get(url)
    data = response.json()
    question = data['results'][0]
    return question

def countdown(): 
    global timeout
    time.sleep(15)
    timeout = True
        
score = 0
timeout = False

while True: 
    q = get_question()
    print("\nQuestion: ", q['question'])
    options = q['incorrect_answers'] + [q['correct_answer']]
    
    import random 
    random.shuffle(options)
    
    for i, opt in enumerate(options): 
        print(f"{i+1}. {opt}")
        
    timeout = False
    thread = threading.Thread(target=countdown)
    thread.start()
     
    answer = input("your answer (number): ")
    if timeout: 
        print("Time's up!")
        break
     
    if options[int(answer)-1] == q['correct_answer']: 
        print("Correct!")
        score += 1
    else: 
        print("Wrong! Correct answer was: ", q['correct_answer'])
        break
    
print("\nGame Over! Your Score: ", score)
