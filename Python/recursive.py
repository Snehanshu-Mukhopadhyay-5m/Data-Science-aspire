# Recurrsion using for factorial
# fact(5) = 5*fact(4)
# fact(4) = 4*fact(3)
# fact(3) = 3*fact(2)
# fact(2) = 2*fact(1)
# fact(1) = 1*fact(0) return 1
# fact(0) = return 1
def fact(n):
    if n == 1 or  n == 0:
        return 1
    else:
        return n*fact(n-1)

num = int(input("Enter number"))
a=fact(num)
print(a)

# fibonacci series using recursion
# 0 1 1 2 3 5 8......n+k-1 n+1 

def fib(n):
    if n == 0 :
        return 0
    if n == 1 :
        return 1
    else:
        return fib(n-1)+fib(n-2)
# this here tell which term is in fibo series like 5th term is 5
num = int(input("Which terms is in fibo seies:"))
a = fib(num)

# this prints the series of fibonacci series
print(a)
for i in range(num+1):
    print(fib(i),end = " ")
