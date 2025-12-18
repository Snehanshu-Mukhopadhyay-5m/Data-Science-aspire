def greatest():
    a = int(input("Enter number1:"))
    b = int(input("Enter number2:"))
    c = int(input("Enter number3:"))
    if a > b and a > c: 
        print(f"{a} is greatest of all")
    elif a < b and b > c: 
        print(f"{b} is greatest of all")
    else:
        print(f"{c} is greatest of all")

n = int(input("Enter how mny times you want to call greatest():"))
for i in range(n+1):
    greatest()