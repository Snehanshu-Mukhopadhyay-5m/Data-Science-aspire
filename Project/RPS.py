# A simple python project for Rock Paper Scissors Game Lets' go

"""
Docstring for Project.RPS

Rock win For Sccissors 
Sccisors win for Paper
Paper Win for Rock

Rock = 1
Paper = 0
Scissors = -1



"""

import random

print("Choose Your Choice\n\tRock : R\n\tScissors : S\n\tPaper : P")
your_choice = input("Enter Your Choice : ")
Choice = {"R":1,"P":0,"S":-1}
your = Choice[(your_choice.upper())]
Computer_choosen = random.choice([-1,0,1])
reverse_Choice_computer = {1:"R",0:"P",-1:"S"}
Computer_choice = reverse_Choice_computer[Computer_choosen]


"""

if(Computer_choosen==1 and your==0):
    print("Computer Choice:",Computer_choice)
    print("Your Choice:",your_choice)
    print("You Wins!!")
elif(Computer_choosen==1 and your==-1):
    print("Computer Choice:",Computer_choice)
    print("Your Choice:",your_choice)
    print("Computer Win!!")
elif(Computer_choosen==0 and your==-1):
    print("Computer Choice:",Computer_choice)
    print("Your Choice:",your_choice)
    print("You Wins!!")
elif(Computer_choosen==0 and your==1):
    print("Computer Choice:",Computer_choice)
    print("Your Choice:",your_choice)
    print("Computer Win!!")
elif(Computer_choosen==-1 and your==0):
    print("Computer Choice:",Computer_choice)
    print("Your Choice:",your_choice)
    print("Computer Win!!")
elif(Computer_choosen==-1 and your==1):
    print("Computer Choice:",Computer_choice)
    print("Your Choice:",your_choice)
    print("You Wins!!")
else:  
    print("Computer Choice:",Computer_choice)
    print("Your Choice:",your_choice)
    if(Computer_choosen == your):
        print("It's Draw")
    else:
        print("Invalid Choice Oops!")

"""


#Another Code 

if((Computer_choosen==1 and your==0) or (Computer_choosen==0 and your==-1) or (Computer_choosen==-1 and your==1)):
    print("Computer Choice:",Computer_choice)
    print("Your Choice:",your_choice)
    print("You Win!!")

elif((Computer_choosen==0 and your==1) or (Computer_choosen==-1 and your==0) or (Computer_choosen==1 and your==-1)):
    print("Computer Choice:",Computer_choice)
    print("Your Choice:",your_choice)
    print("You lose!!")

elif(Computer_choosen == your):  
    print("Computer Choice:",Computer_choice)
    print("Your Choice:",your_choice)
    print("It's Draw")
else:
    print("Invalid Choice Oops!")
