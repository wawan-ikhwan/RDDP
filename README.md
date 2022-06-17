# RDDP
RDDP (Remote Desktop Datagram Protocol) is similar like RDP (Remote Desktop Protocol) but using UDP as main protocol instead of TCP/IP, most care about speed and low latency at cost of quality due to compression.

Protocol Rule:
1. Client send ```ACK``` to addrPortServer periodically every 3 seconds.
2. Server receive ```ACK``` and got addrPortClient
3. Server send ```SYN``` to addrPortClient
4. Server send ```<ENCRYPTED IMAGE>``` to addrPortClient
5. Client check if ```SYN``` then reserve buffer (bytesReceived) otherwise fill the buffer.
6. Client know if the data completed transfer if length of bytesFromServer is not equal to 508 (payload size).
