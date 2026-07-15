import base64
import sys

src = sys.argv[1]
dest = sys.argv[2]

with open(src, 'r') as f:
    content = f.read().strip()

if content.startswith('Result: "'):
    content = content[9:]
    if content.endswith('"'):
        content = content[:-1]

data = base64.b64decode(content + '==', validate=False)
with open(dest, 'wb') as f:
    f.write(data)
print(f'Saved: {len(data)} bytes to {dest}')
