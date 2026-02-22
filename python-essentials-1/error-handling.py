

try:
    n1 = int(input("Enter first number:"))
    n2 = int(input("Enter second number:"))
    sumRes = n1+n2
    divRes = n1//n2
except ValueError:
    print("Invalid Input")
except ZeroDivisionError:
    print("Cannot divide by zero")
else:  
    print(f"Sum: {sumRes}")
    print(f"Division: {divRes}")
