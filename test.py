data = b'abcdefghi'
info = [data[i:i+2] for i in range(0, len(data), 2)]

print(info)