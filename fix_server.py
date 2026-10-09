import re

with open('server.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    if '"solution": "' in line and '",' not in line and '"\n' not in line:
        # It's an unclosed string. We combine it with the next line
        if i + 1 < len(lines):
            next_line = lines[i+1].lstrip() # remove indentation from next line
            # Join with \n literally
            line = line.rstrip('\n') + '\\n' + next_line
            i += 1
    new_lines.append(line)
    i += 1

with open('server.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
