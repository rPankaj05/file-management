import random
import string

def generate_password(length):
    """Generate a password of given length with letters and numbers"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def is_valid_password(password):
    """Check if password meets complexity requirements"""
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    return has_upper and has_lower and has_digit

def main():
    print("Password Generator - 7 or 8 characters (letters and numbers only)")
    print("=" * 50)
    
    while True:
        # Randomly choose between 7 and 8 characters
        length = random.choice([7, 8])
        
        # Generate password
        password = generate_password(length)
        
        # Check if valid
        if is_valid_password(password):
            print(f"\nValid password generated: {password}")
            print(f"Length: {length} characters")
            print(f"Contains at least one uppercase, one lowercase, and one number")
            break
            
        # Uncomment the next line to see all attempted passwords
        # print(f"Tried: {password} (invalid)")

if __name__ == "__main__":
    main()