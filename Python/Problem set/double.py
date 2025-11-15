string = "This is a sentence written  where  the chacters have  double space   and now we will detect"
double_space = string.find("  ")
print(double_space)
print(string.replace("  ", " "))