from pprint import pprint

latex = r"\left(54+\frac{31i}{4}\right)^{2+4}-\left(4i\cdot\left(\frac{3+i}{6}\right)\right)^{3}+4"
# Remove \left and \right because they are purely for formatting
latex = latex.replace(r"\left", "").replace(r"\right", "")

digits = "0123456789."
constants = ["i", "e", r"\pi"]
tokens = ["(", ")", "{", "}", "^", r"\frac",
          r"\cdot", "+", "*", "-"] + constants


def tokenize(latex):
    tokenized = []
    unparsed = ""
    for character in latex:
        if character not in digits:
            # Check whether this is the end of a number
            try:
                x = float(unparsed)
                tokenized.append(x)
                unparsed = ""
            except:
                pass
        unparsed += character
        if unparsed in tokens:
            tokenized.append(unparsed)
            unparsed = ""

    # Check whether a number wasn't tokenized
    try:
        x = float(unparsed)
        tokenized.append(x)
    except:
        pass

    return tokenized


def parser(tokens):
    # Pass 1: Make parentheses be parentheses
    def parse_parentheses(to_parse):
        parentheses_level = 0
        parentheses_start = 0
        result = []
        for i, t in enumerate(to_parse):
            if parentheses_level == 0 and t not in ["(", ")"]:
                result.append(t)
            elif t == "(":
                parentheses_level += 1
                if parentheses_level == 1:
                    parentheses_start = i
            elif t == ")":
                parentheses_level -= 1
                if parentheses_level == 0:
                    result.append(parse_parentheses(
                        to_parse[(parentheses_start + 1):i]
                    ))
        return result

    parenthesized = parse_parentheses(tokens)

    # Pass 2: make groups be groups, and check what each token is
    def parse_groups(to_parse):
        grouped = []
        group_start = []
        for i, t in enumerate(to_parse):
            if t == "{":
                group_start.append(i)
            elif t == "}":
                start = group_start.pop() + 1
                grouped.append({
                    "type": "group",
                    "items": parse_groups(
                        to_parse[start:i]
                    )
                })
            elif len(group_start) == 0 and type(t) is list:
                grouped.append({
                    "type": "brackets",
                    "items": parse_groups(t)
                })
            elif len(group_start) == 0:
                val_type = "undetermined"

                if type(t) is float:
                    val_type = "number"
                elif t in constants:
                    val_type = "constant"

                grouped.append({
                    "type": val_type,
                    "v": t
                })

        return grouped

    grouped = parse_groups(parenthesized)

    # Pass 3: make fractions be fractions
    def parse_fractions_rec(to_parse):
        index = 0
        parsed = []
        while index < len(to_parse):
            val = to_parse[index]

            if val["type"] in ["brackets", "group"]:
                parsed.append({
                    "type": val["type"],
                    "items": parse_fractions_rec(val["items"])
                })
            elif val["type"] == "undetermined" and val["v"] == r"\frac":
                parsed.append({
                    "type": "fraction",
                    "items": [
                        parse_fractions_rec([to_parse[index + 1]])[0],
                        parse_fractions_rec([to_parse[index + 2]])[0]
                    ]
                })
                index += 2
            else:
                parsed.append(to_parse[index])
            index += 1

        return parsed

    fractioned = parse_fractions_rec(grouped)

    def parse_operator_rec(to_parse, operator_variants, operator_name):
        index = 0
        parsed = []
        while index < len(to_parse):
            val = to_parse[index]
            if index < (len(to_parse) - 2) \
                    and to_parse[index + 1]["type"] == "undetermined" \
                    and to_parse[index + 1]["v"] in operator_variants:
                parsed.append({
                    "type": operator_name,
                    "items": [val, to_parse[index + 2]]
                })
                index += 3
            else:
                if "items" in val:
                    parsed.append({
                        "type": val["type"],
                        "items": parse_operator_rec(
                            val["items"],
                            operator_variants,
                            operator_name
                        )
                    })
                else:
                    parsed.append(val)
                index += 1
        return parsed

    def parse_implied_multiplication(to_parse, is_frac=False):
        index = 0
        parsed = []
        while index < len(to_parse):
            val = to_parse[index]
            if index < len(to_parse) - 1 \
                    and to_parse[index]["type"] != "undetermined" \
                    and to_parse[index + 1]["type"] != "undetermined":
                parsed.append({
                    "type": "multiplication",
                    "items": [val, to_parse[index + 1]]
                })
                index += 2
            else:
                if "items" in val:
                    parsed.append({
                        "type": val["type"],
                        "items": parse_implied_multiplication(
                            val["items"],
                            is_frac=val["type"] == "fraction"
                        )
                    })
                else:
                    parsed.append(val)
                index += 1
        return parsed

    # Pass 4: Implied multiplication when there is no operator
    implicitly_multiplied = parse_implied_multiplication(fractioned)
    # Pass 5: powers
    powered = parse_operator_rec(implicitly_multiplied, ["^"], "power")
    # Pass 6: multiplication
    multiplied = parse_operator_rec(powered, ["*", r"\cdot"], "multiplication")
    # Pass 7: addition
    added = parse_operator_rec(multiplied, ["+"], "addition")

    def parse_unary_negative(to_parse):
        index = 0
        parsed = []
        while index < len(to_parse):
            val = to_parse[index]
            if index == 0 and len(to_parse) == 2 \
                    and to_parse[0]["type"] == "undetermined" \
                    and to_parse[1]["type"] != "undetermined":
                return [{
                    "type": "negative",
                    "items": [val]
                }]
            else:
                if "items" in val:
                    parsed.append({
                        "type": val["type"],
                        "items": parse_unary_negative(
                            val["items"]
                        )
                    })
                else:
                    parsed.append(val)
                index += 1
        return parsed
    # Pass 8: unary negative
    unary_negatived = parse_unary_negative(added)
    # Pass 9: subtraction
    subtracted = parse_operator_rec(unary_negatived, ["-"], "subtraction")

    def remove_undetermined(to_parse):
        parsed = []
        for val in to_parse:
            if val["type"] == "undetermined":
                continue
            elif "items" in val:
                parsed.append({
                    "type": val["type"],
                    "items": remove_undetermined(val["items"])
                })
            else:
                parsed.append(val)
        return parsed
    # Pass 10: remove all undetermined
    return remove_undetermined(subtracted)[0]

print(parser(tokenize(latex)))
