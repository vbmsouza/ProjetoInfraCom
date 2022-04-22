# server
# Conexao UDP implementada com socket e algoritmo CHECKSUM
# Equipe 7 
# Alunos: Renan Guilherme Siqueira de Araújo, Flávio José Canuto de Vasconcelos Júnior, Vinícius Pereira de Araújo e 
#         Victor Bruno de Moura Souza. 

import socket
import struct
from time import sleep

def carry(a, b):
    c = a + b
    return (c & 0xffff) + (c >> 16)

def checksum_calc(msg):
    s = 0
    if len(msg) % 2 == 0:
        pass
    else:
        msg = msg + 's'
    for i in range(0, len(msg), 2):
        w = ord(msg[i]) + (ord(msg[i+1]) << 8)
        s = carry(s, w)
    return ~s & 0xffff


source_port = 12000
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('', source_port))
print("[STARTING SERVER]...")
sleep(3)
print("[READY FOR CONNECTIONS]")
while True:
    data, address = server_socket.recvfrom(1024)
    print(f"[CONNECTION ESTABLISHED] - {address}")
    
    data = data.decode().upper() # novo dado que sera enviado para o cliente
    packet = data
    data_length = len(packet) # tamanho do novo dado que ser enviado ao cliente
    checksum = checksum_calc(packet) # checksum dos dados que serao enviado
    udp_header = struct.pack("!IIII", source_port, address[1], data_length, checksum) # dando packet com os 4 elementos

    full_packet = udp_header + packet.encode() # juntando o header com os dados

    server_socket.sendto(full_packet, address) # enviando para o cliente
