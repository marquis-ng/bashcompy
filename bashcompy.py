indent = " " * 4

from sys import argv, executable, stdout
from os.path import isfile, isdir
from os import system
from re import match

try:
    from yaml import safe_load
except:
    try:
        assert not system(f"{executable} -m pip install pyyaml")
        from yaml import safe_load
    except:
        exit(4)

def print(*strings, indent_lvl=0):
    for string in [""] if len(strings) == 0 else strings:
        if write2file:
            global writebuffer
            writebuffer += "\n" if string == "" else f"{indent * indent_lvl}{string}\n"
        else:
            __builtins__.print("" if string == "" else indent * indent_lvl + string)

write2file = False
writebuffer = ""

if len(argv) == 3:
    write2file = True
    if isdir(argv[2]):
        exit(3)
elif len(argv) != 2:
    exit(1)

if not isfile(argv[1]):
    exit(2)

with open(argv[1], "r") as infile:
    data = safe_load(infile)
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

if write2file:
    with open(argv[2], "w") as outfile:
        outfile.write(writebuffer)
