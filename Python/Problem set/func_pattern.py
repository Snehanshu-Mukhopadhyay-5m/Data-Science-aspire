'''
***
**
*
'''



def pattern():
    n = int(input("Enter number to print pattern:"))
    for i in range(0,n):
        print("*"*(n-i))
        # print("*"*(i+1))
pattern()