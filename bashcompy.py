indent = " " * 4

from sys import argv
from os.path import isfile
from yaml import safe_load
from re import match

def print(*strings, indent_lvl=0):
    for string in [""] if len(strings) == 0 else strings:
        __builtins__.print("" if string == "" else indent * indent_lvl + string)

if len(argv) != 2:
    exit(1)
elif not isfile(argv[1]):
    exit(2)

data = safe_load(open(argv[1], "r"))
commands = sorted(data.keys(), reverse=True, key=lambda string: " " not in string or "*" in string)

print(f"_{commands[0]}_completions_filter() {{")
print("local words=\"$1\"", "local cur=${COMP_WORDS[COMP_CWORD]}", "local result=()", "",
    "if [ \"${cur:0:1}\" = \"-\" ]; then", f"{indent}echo \"$words\"",
    "else", f"{indent}for word in $words; do", f"{indent * 2}[ \"${{word:0:1}}\" != \"-\" ] && result+=(\"$word\")", f"{indent}done", "",
    "echo \"${result[*]}\"", "fi", indent_lvl=1)
print("}", "")

print(f"_{commands[0]}_completions() {{")
print("local cur=${COMP_WORDS[COMP_CWORD]}",
    "local compwords=(\"${COMP_WORDS[@]:1:$COMP_CWORD-1}\")",
    "local compline=\"${compwords[*]}\"","",
    "case \"$compline\" in", indent_lvl=1)

for command in commands[1:] + [commands[0]]:
    print(("\"" + " ".join(command.split()[1:]).replace("*", "\"*\"") + "\"" + ("" if "*" in command else "*") + ")").replace("\"\"*)", "*)"), indent_lvl=2)
    print("while read -r; do", f"{indent}COMPREPLY+=(\"$REPLY\")",
        f"done < <(compgen {''.join([f'-A {string[1:-1]} ' for string in data[command] if match('^<.+>$', string)])}\
-W \"$(_{commands[0]}_completions_filter \"{' '.join([string for string in data[command] if not match('^<.+>$', string)])}\")\" -- \"$cur\")".replace(f"-W \"$(_{commands[0]}_completions_filter \"\")\" ", ""), ";;", indent_lvl=3)

print(f"{indent}esac", "}", f"complete -F _{commands[0]}_completions {commands[0]}")
