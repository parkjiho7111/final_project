import json
import re

# Read the file
with open('policies_remake.json', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix line 9529 - remove embedded newline in genre field
lines[9528] = '    "genre": "취업/직무",\n'

# Fix line 9530 - fix region field
lines[9529] = '    "region": "충남",\n'

# Write back
with open('policies_remake.json', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Fixed problematic lines")

# Now try to parse
with open('policies_remake.json', 'r', encoding='utf-8') as f:
    try:
        data = json.load(f)
        print(f"✓ JSON is now valid! Found {len(data)} records.")
    except json.JSONDecodeError as e:
        print(f"✗ Still has error: {e}")
        print(f"  Error at line {e.lineno}, column {e.colno}")
