# Function call for average of 3 number

def avg():
    a = int(input("Enter number 1:"))
    b = int(input("Enter number 2:"))
    c = int(input("Enter number 3:"))

    print("Avg:",(a+b+c)/3)
def call():
    n = int(input("Enter how many time s you want to call avg()"))
    for i in range(n):
        avg()

call()

# Function call to greet the user using function

def greet():
    name = input("Enter name:")
    print(f"Good Morning {name}!.\n{name} waht can I hep you with")
greet()


# Function calling by an argument

def greet(name):
    print(f"Good Morning {name}!.\n{name} what can I help you with today")

name = input("Enter name:")
greet(name)


# Function calling by two argument

def greet(name,profile):
    print(f"Hi, myself {name}!.\nI am {profile}")

name = input("Enter name:")
profile = input("Enter profile:")
greet(name,profile)


# Function calling by one default argument

def greet(name,profile="programmer"):
    print(f"Hi, myself {name}!.\nI am {profile}")

name = input("Enter name:")
greet(name)


