n = int(input("Enter number:"))
fact = 1
for i in range(1,n+1):
    fact = fact*(i)
    
print(fact)

i = 1
fact = 1
while (i<n+1):
    fact *= i
    i+=1
print(fact)