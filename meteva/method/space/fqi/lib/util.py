import copy


def get_attributes(x):
    attribute = copy.deepcopy(x)
    attribute.pop('X')
    attribute.pop('Xhat')
    return attribute
