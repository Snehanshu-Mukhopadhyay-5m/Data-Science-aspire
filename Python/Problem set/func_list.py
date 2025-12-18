def remove_from_list_strip(word):
    n = []
    list = ["Jai","Harsh","Varun "]
    for i in list:
        if not(i == word):
            n.append(i.strip(word))
            
    return n
word = input("Enter word")
print(remove_from_list_strip(word))