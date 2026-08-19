def complex_decision_matrix(a, b, c, d, mode, flag, items):
    """High cyclomatic complexity function with multiple branches and nested loops."""
    result = 0

    if mode == "A":
        if flag:
            for item in items:
                for sub_item in item.get("sub_items", []):
                    for leaf in sub_item.get("leaves", []):
                        if leaf.get("val") > 10:
                            if a > b and c < d:
                                result += leaf.get("val") * 2
                            elif a == b:
                                result += leaf.get("val") + 1
                            else:
                                result -= 1
                        else:
                            if mode != "B" and flag:
                                result += 5
        else:
            if a > 100:
                result = 100
            elif a > 50:
                result = 50
            elif a > 20:
                result = 20
            else:
                result = 0
    elif mode == "B":
        while a > 0:
            while b > 0:
                while c > 0:
                    c -= 1
                    result += 1
                b -= 1
            a -= 1
    elif mode == "C":
        if a and b or c and not d:
            result = 42
        elif not a and (b or c):
            result = 24
        else:
            result = 12
    else:
        result = -1

    return result
