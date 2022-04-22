# cliente
# Conexao UDP implementada com socket e algoritmo CHECKSUM
# Equipe 7 
# Alunos: Renan Guilherme Siqueira de Araújo, Flávio José Canuto de Vasconcelos Júnior, Vinícius Pereira de Araújo e 
#         Victor Bruno de Moura Souza. 

import socket
import zlib
import struct

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



client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
message = input("Digite uma mensagem para o servidor: ")
addr = ("10.0.0.143", 12000) # mudar o ip de acordo com o localhost da maquina que hospeda o servidor

client_socket.sendto(message.encode(), addr)
    
packet, server = client_socket.recvfrom(1024) 
udp_header = packet[:16] # os primeiros 16 espacos alocados sao os headers

data = packet[16:] # os 16 ultimos espacos sao os dados

udp_header = struct.unpack("!IIII",udp_header) #dando unpack e colocando 4 elementos em udp_header 0-source port 1- destination port 2- tamanhon do dado 3- checksum
right_checksum = udp_header[3] #pegando o checksum enviado.

checksum = checksum_calc(data.decode()) # calculando o novo checksum da msg que chegou

data_length = len(data)
correct_data_length = udp_header[2]

if checksum != right_checksum:
    print("[WRONG DATA !]")
elif correct_data_length != data_length:
    print("PACKET LENGTH WAS MODIFIED")
else:
    print(f"[CHECKSUM RECEIVED = {right_checksum}]\n[NEW CHECKSUM = {checksum}]\n")
    print(f"[DATA LENGTH RECEIVED = {correct_data_length}]\n[NEW DATA LENGTH = {data_length}]\n")
    print(f"DATA: {data.decode()}")

client_socket.close()
    