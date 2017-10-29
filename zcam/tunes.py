def noah(list_):
    '''Transforms a flat list into a list of 2-tuples'''

    listiter = iter(list_)
    return list(zip(listiter, listiter))

TUNE_BEEP = noah('261 0.2 0 0.8'.split())
TUNE_ARMED = noah('261 0.2 0 0.01 261 0.2 0 0.01 349.2 0.2'.split())
TUNE_DISARMED = noah('349.2 0.2 0 0.01 349.2 0.2 0 0.01 261 0.2'.split())
TUNE_ERROR = noah('261 0.2 0 0.01 220 0.2 0 0.01 73.42 0.5'.split())
