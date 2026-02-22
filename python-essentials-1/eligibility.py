try:
    name = input("Enter your name: ")
    try:
        age = int(input("Enter your age: "))
    except ValueError:
        raise ValueError("Invalid age input")
    
    if age < 0:
        raise ValueError("Age cannot be negative")

    stmt = ""
    if age < 13:
        stmt = "You are a Child"
    elif age >= 13 and age <= 17:
        stmt = "You are a Teenager"
    elif age >= 18 and age <= 59:
        stmt = "You are an Adult"
    else:
        stmt = "You are a Senior Citizen"
except ValueError as e:
    print(e)
else:
    print(f"Hello {name}")
    print(stmt)
    if age >= 18:
        print("You are eligible to vote")
    else:
        print("You are not eligible to vote")