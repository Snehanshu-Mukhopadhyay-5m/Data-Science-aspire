name = input("Enter your name: ")
date = input("Enter the date: ")
# print(f"Dear {name}\nYou are selected \n{date}.")

letter = "Dear <|name|>,\
    \nYou are selected!\
    \n<|date|>."
print(letter.replace("<|name|>", name).replace("<|date|>", date))
