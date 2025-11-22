# Table printing using for loop
n = int(input("Enter number:"))
print(f"\n\tTable of {n}\n")
for i in range(11):
    print(f"\t{i} X {n} = {i*n}")

# Table printing using while loop
n = int(input("Enter number:"))
print(f"\n\tTable of {n}\n")
i = 0
while (i<11):
    print(f"\t{i} X {n} = {i*n}")
    i += 1