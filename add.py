def add():
  try:
    num1 = float(input("Enter first number: "))
    num2 = float(input("Enter second number: "))
    
    result = num1 + num2
    print(f"The sum of {num1} and {num2} is {result}")
  except ValueError:
    print("Invalid input. Please enter numeric values.")
if __name__ == "__main__":
  add()