n = int(input("Enter number:"))
i = 0
sum = 0
while (i<=n):
    sum += i
    i+=1
print("sum using for while for first n natural number",sum)



total = 0
for j in range(1,n+1):
    total += j
print("sum using for loop for first n natural number",total)