name = "Harry Potter and the Chamber of Secrets"
name1 = name[0:] 
name2 = name[2:18]
name3 = name[18:2:-1]
name4 = name[:5] + name[6:12]
name5 = name[-7:]
name6 = name[-7::-1]
name7 = name5[:-8:-1]
# print(name7)
print(len(name))
print(name.endswith("s"))
print(name.startswith("H")) #if "h" and not "H" then it will return false
print(name.replace("Harry", "Ron"))
print(name.find("Chamber"))