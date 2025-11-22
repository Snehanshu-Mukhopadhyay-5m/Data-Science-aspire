n = int(input("Enter number:"))
# while (n%2==0):
#     print("prime")
#     break
# else:
#     print("not prime")

if n<2:
    print("not prime")
else:
    for i in range(2,n):
        if n%i == 0:
            print("not prime")
            break
    else:
        print("prime")

