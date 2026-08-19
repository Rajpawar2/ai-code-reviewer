def append_to_list(val, my_list=[]):
    """Bug: Mutable default argument accumulates state across calls."""
    my_list.append(val)
    return my_list


def divide_numbers(a, b):
    """Bug: Bare except hides ZeroDivisionError, SystemExit, and typing issues."""
    try:
        res = a / b
        return res
    except:
        pass


def calculate_discount(price, discount=None):
    """Bug: '== None' comparison and unreachable code."""
    if discount == None:
        discount = 0.0
        return price
        # Dead code
        extra_discount = 5.0
        price -= extra_discount

    return price * (1 - discount)


def process_user_record(user_data):
    """Bug: Accessing undefined variable and direct True comparison."""
    is_admin = user_data.get("is_admin") == True
    if is_admin:
        role = "Administrator"
    
    # Bug: role may be unbound if is_admin is False
    return {"status": "success", "user_role": role}
