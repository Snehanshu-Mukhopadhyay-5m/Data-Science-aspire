a =int(input("Enter first number: "))
name = input("Enter your name: ")

if (a>18):
    print(f"{name} eligible to vote")
elif (a==18):
    print(f"{name} just eligible to vote")
elif (a<0):
    print("Invalid age")   
else:
    print(f"{name} not eligible to vote")