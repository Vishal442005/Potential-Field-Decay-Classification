with open('restyle_and_scale_remaining.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for l in lines:
    if l.strip().startswith('print(" -> Saved figures/') and not l.strip().endswith(')'):
        l = l.rstrip() + ')\n'
    new_lines.append(l)

with open('restyle_and_scale_remaining.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

import ast
ast.parse(''.join(new_lines))
print('Successfully fixed and parsed restyle_and_scale_remaining.py')
