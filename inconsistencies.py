from glob import glob

from strec.garabik import parse_config

for fname in glob("../grc/colourfiles/conf.*"):
    with open(fname) as fptr:
        data = fptr.read()
    try:
        rules = parse_config(data)
    except Exception as exc:
        print(f"unable to parse {fname} ({exc})")
        continue

    num_errors = 0
    for rule in rules:
        if len(rule.colors) != rule.regex.groups:
            num_errors += 1
    print(f"--- {fname} {num_errors}")
    for rule in rules:
        if len(rule.colors) != rule.regex.groups:
            print(f" ERROR: {rule.regex.pattern}")
            print(f"      | {rule.colors}")
