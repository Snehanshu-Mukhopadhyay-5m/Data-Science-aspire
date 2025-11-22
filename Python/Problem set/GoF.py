a = int(input("Enter first number: "))
b = int(input("Enter second number: "))
c = int(input("Enter third number: "))
d = int(input("Enter first number: "))

if  (a > b) and (a > c) and (a > d):
    print(f"{a} is the greatest number")
elif  (b > a) and (b > c) and (b > d):
    print(f"{b} is the greatest number")
elif  (c > a) and (c > b) and (c > d):
    print(f"{c} is the greatest number")
else:
    print(f"{d} is the greatest number") 