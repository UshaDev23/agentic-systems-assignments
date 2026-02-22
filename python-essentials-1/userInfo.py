try:
    firstName = input("Enter first name: ")
    lastName = input("Enter last name: ")
    try:
        age = int(input("Enter Age: "))
    except ValueError:
        raise ValueError("Invalid input")

    if age < 0:
        raise ValueError("Age cannot be negative")
   
    fullName = firstName +" "+ lastName
    
except ValueError as e:
    print(e)
else:
    print(f"Full Name: {fullName}")
    print(f"You will be {age+1} next year")


