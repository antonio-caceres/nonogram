
import json


def parse_rule_input():
    print("For each rule, input the line lengths separated by spaces.\n"
          "Conclude rule entry by entering a new line.\n"
          "(Enter \"0\" for a rule without any lines.)")
    rules = []
    while row := input("> "):
        rules.append([int(token) for token in row.split()])
    return rules


def rule_input():
    title = "JSON Nonogram Input Script"
    print(title + "\n" + "-" * len(title))

    name = input("Nonogram Name: ")

    print("Input Row Rules.")
    rows = parse_rule_input()
    print("Input Column Rules.")
    cols = parse_rule_input()

    return {
        "name" : name,
        "clues" : {
            "row" : rows,
            "col" : cols,
        },
    }


if __name__ == "__main__":
    print(json.dumps(rule_input()))
