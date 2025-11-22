name = input("Enter Name: ")
sub1 = int(input("Enter marks of subject 1: "))
sub2 = int(input("Enter marks of subject 2: "))
sub3 = int(input("Enter marks of subject 3: "))

total = 450
marks_total = sub1 + sub2 + sub3
per = (marks_total/total)*100

if (per) == 40 and (sub1==sub2==sub3) == 33: 
    print(f"{name} has passed the exam with 40% and 33% in each subject")
elif 60 >= (per) >= 40 and (60>=sub1>=33 and 60>=sub2>=33 and 60>=sub3>=33):
    print(f"{name} has passed the exam with {per}% Good")
elif (per) > 60 and (sub1>60 and sub2>60 and sub3>60):
    print(f"{name} has passed the exam with {per}% Excellent")
elif (per) < 40 or (sub1<33 or sub2<33 or sub3<33):
    print(f"{name} has failed the exam with {per}%")
elif ((per) == 100 and (sub1==sub2==sub3)==100) or (80 <= (per) < 100 and (sub1>80 and sub2>80 and sub3>80)):
    print(f"{name} has passed the exam with {per}% Outstanding")
else:
    print("Invalid Input")

