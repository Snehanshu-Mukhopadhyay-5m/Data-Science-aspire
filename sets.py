s = {1, 2, 3, 4, 5}

e = set() #this will create an empty set not this e = {} which will create an empty dictionary
print(s)
print(len(s))
print(type(s))
# print(s.remove(11)) #removes 3 from the set


s1 = {4, 5, 6, 7, 8}
s2 = {1, 2, 3, 4, 5}

print(s1.union(s2)) #combines both sets and removes duplicates
print(s1.intersection(s2)) #returns only the common elements in both sets
print(s1.difference(s2)) #returns only the elements in s1 that are not in s2
print(s1.issubset(s2)) #checks if s1 is a subset of
print(s1.issuperset(s2)) #checks if s1 is a superset of s2
s2.update({6,7,8}) #adds multiple elements to the set
print(s2-s1)

s1.issubset({5})
