marks = {
    "Shyam" : 56,
    "Mohan" : 78,
    "Ramesh" : 90
}
print(marks,type(marks))
print(marks["Mohan"])

print(marks.items())
print(marks.keys())
print(marks.values())
print( marks.update({"Ramesh": 88}))
print(marks.pop("Shyam"))
print(marks)


