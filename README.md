# RDDP
RDDP (Remote Desktop Datagram Protocol) is similar like RDP (Remote Desktop Protocol) but using UDP as main protocol instead of TCP/IP, most care about speed and low latency at cost of quality due to compression.

Protocol Rule:
1. Client send ```b'TRX'``` to addrPortServer
2. Server got addrPortClient
3. Server send ```b'SYN'``` to addrPortClient
4. Server send ```b'<ENCRYPTED IMAGE>'``` to addrPortClient
5. Client check if ```b'SYN'``` then reserve buffer (bytesReceived) otherwise fill the buffer.
6. Client know if the data completed transfer if length of bytesFromServer is not equal to 508 (payload size).
