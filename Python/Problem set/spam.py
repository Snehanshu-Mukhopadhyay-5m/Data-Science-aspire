message = input("Enter a message: ")
spam1 = "Make a lot of money" 
spam2 = "Buy now" 
spam3 = "Click this" 
spam4 = "Subscribe this" 
spam5 = "Free gift"

if spam1 in message or spam2 in message or spam3 in message or spam4 in message or spam5 in message:
    print("This message is considered spam.")
else:
    print("This message is not considered spam.")