from password_generator import generate_password, check_password_strength

password = generate_password(12, True, True, True, True)

print("Generated Password:", password)
print("Password Strength:", check_password_strength(password))