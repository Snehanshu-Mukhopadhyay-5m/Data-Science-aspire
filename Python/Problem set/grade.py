marks = int(input("Enter your marks: "))
if 100 >= marks >= 90:
    grade = 'Excellent'
    print(grade)
elif 90 >= marks >= 80:
    grade = 'A'
    print(grade)
elif 80 >= marks >= 70:
    grade = 'B'
    print(grade)
elif 70 >= marks >= 60:
    grade = 'C'
    print(grade)
elif 60 >= marks >= 50:
    grade = 'D'
    print(grade)
else:
    grade = 'F'
    print(grade)