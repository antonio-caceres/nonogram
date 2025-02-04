
import json


def parse_rule_input():
    print("For each rule, input the line lengths separated by spaces.\n"
          "Enter an empty rule to conclude the nonogram.")
    rules = []
    while row := input(""):
        rules.append([int(token) for token in row.split()])
    return rules



if __name__ == "__main__":
    title = "JSON Nonogram Input Script"
    print(title + "\n" + "-" * len(title))

    name = input("Nonogram Name: ")

    print("Input Row Rules.")
    rows = parse_rule_input()
    print("Input Column Rules.")
    cols = parse_rule_input()

    print(json.dumps({
        "name" : name,
        "height" : len(rows),
        "width" : len(cols),
        "clues" : {
            "row" : rows,
            "col" : cols,
        },
    }))


