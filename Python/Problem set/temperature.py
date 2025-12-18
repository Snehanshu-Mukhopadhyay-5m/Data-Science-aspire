def Celsius():
    F = int(input("Enter Fahrnheit value:"))
    C = (F - 32) * 5/9
    print("Fahrenheit to celcius:",C)

def Fahrenheit():
    C = float(input("Enter Celcius value:"))
    F = (C * 9/5) + 32
    print(f"Celcius to Fahrenheit:{F:.2f}")

def choose():
    choose = input("Select 'C' or 'F':")
    if (choose.lower() == "c"):
        Celsius()
    elif (choose.lower() == "f"):
        
        Fahrenheit()
    else:
        return 0
choose()