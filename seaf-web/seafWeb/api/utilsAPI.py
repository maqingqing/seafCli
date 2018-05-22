import math

def convertBytes(bytes, lst=['bytes', 'KB', 'MB', 'GB', 'TB', 'PB']):
    if bytes <= 0:
        return ('%.1f' + " " + lst[1]) % 0
    i = int(math.floor(math.log(bytes, 1024)))

    if i >= len(lst):
        i = len(lst) - 1
    return ('%.1f' + " " + lst[i]) % (bytes/math.pow(1024, i))