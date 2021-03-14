# -*-coding:utf-8-*-


def get_attributes_for_feat(feat):
    attribute = {'Type': feat['Type'], 'xrange': feat['xrange'], 'yrange': feat['yrange'],
                 'dim': feat['dim'], 'xstep': feat['xstep'], 'ystep': feat['ystep'], 'area': feat['area'],
                 'warnings': feat['warnings'], 'xcol': feat['xcol'], 'yrow': feat['yrow']}
    return attribute


def remove_key_from_list(origin_list, remove_list):
    for i, val in enumerate(remove_list):
        origin_list.remove(val)
    return origin_list
