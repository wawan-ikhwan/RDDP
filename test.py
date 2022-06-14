a = [b'\x01bacot',b'\x02kau',b'\xffboleh']

print(b''.join(a))


print(int.from_bytes(int.to_bytes(1,1,'little'),'little'))