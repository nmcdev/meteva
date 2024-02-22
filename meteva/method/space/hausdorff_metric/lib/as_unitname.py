def as_unitname(s):
    n = 0
    if s is not None:
        n = len(s)
    if n > 3:
        raise Exception("Unit name should be a character string,", "or a vector/list of 2 character strings,",
                        "or a list(character, character, numeric)")
    # out = switch(n + 1, makeunitname(), makeunitname(s[[1]], s[[1]]), makeunitname(s[[1]], s[[2]]), makeunitname(s[[1]], s[[2]], s[[3]]))
    out = None
    if n == 0:
        out = makeunitname()
    elif n == 1:
        out = makeunitname(s[[0]], s[[0]])
    elif n == 2:
        out = makeunitname(s[[0]], s[[1]])
    elif n == 3:
        out = makeunitname(s[[0]], s[[1]], s[[2]])
    return out


def makeunitname(sing="unit", plur="units", mul=1):
    out = {
        'singular': sing,
        'plural': plur,
        'multiplier': mul
    }
    return out
