import bcrypt

pwd = 'password123'
hash_val = '$2b$12$rE90qSO9zWbGdDHInqwc5e3sLi5JSpbWflrRYD4vRU/9vYrlXbWz6'

try:
    result = bcrypt.checkpw(pwd.encode(), hash_val.encode())
    print(f'✓ Hash is VALID for password123: {result}')
except Exception as e:
    print(f'✗ Hash validation failed: {e}')

# Generate a fresh hash
new_hash = bcrypt.hashpw(pwd.encode(), bcrypt.gensalt(rounds=12))
print(f'\n✓ Fresh hash generated: {new_hash.decode()}')

# Test the fresh hash
result2 = bcrypt.checkpw(pwd.encode(), new_hash)
print(f'✓ Fresh hash verified: {result2}')
