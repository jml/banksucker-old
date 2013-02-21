

def select(xs, key, value):
    for x in xs:
        if x[key] == value:
            return x
    return None


def by_name(xs, value):
    return select(xs, 'name', value)
