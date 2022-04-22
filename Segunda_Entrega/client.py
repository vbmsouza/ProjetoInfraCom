# cliente
# Conexao UDP implementada com socket e algoritmo CHECKSUM
# Equipe 7 
# Alunos: Renan Guilherme Siqueira de Araújo, Flávio José Canuto de Vasconcelos Júnior, Vinícius Pereira de Araújo e 
#         Victor Bruno de Moura Souza. 

import socket
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

def not_corrupted (packet,seqNumber,type):

    udp_header = packet[:16]
    data = packet[16:]

    udp_header = struct.unpack("!IIII",udp_header)
    data_checksum = checksum_calc(data.decode())
    
    checksum = udp_header[3]
    data_seqNumber = udp_header[2]

    if checksum != data_checksum:
        return False

    if type == 'sender' and seqNumber != data_seqNumber:

        return False

    if type == 'sender':
        seqNumber = update_seq_number(seqNumber)

    return True

def make_pkt(source_port,dest_port,seqNumber,msg):

    
    checksum = checksum_calc(msg) # checksum dos dados que serao enviado
    udp_header = struct.pack("!IIII", source_port, dest_port, seqNumber, checksum) # dando packet com os 4 elementos

    full_packet = udp_header + msg.encode() # juntando o header com os dados
    
    return full_packet

def update_seq_number(seqNumber):
        seqNumber = (seqNumber + 1)%2
        return seqNumber
seqNumber = 0
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print("PRESS 1 TO RECEIVE THE MENU: ")
addr = ("10.0.0.143", 12000) # mudar o ip de acordo com o localhost da maquina que hospeda o servidor
source_port = 12000

while 1:
    ack = False
    message = input()
    client_socket.settimeout(1)

    while not ack:
        client_socket.sendto(make_pkt(source_port,addr[1],seqNumber,message), addr)

        try:
            packet, server = client_socket.recvfrom(1024)
            print(packet[16:]) 
        except socket.timeout:
            print("ESTOURO DE TEMPO")
        else:
            ack = not_corrupted(packet,seqNumber,'sender')
            print(ack)

    client_socket.settimeout(None)

    packet, server = client_socket.recvfrom(1024) 
    data = packet[16:]

    if  not_corrupted(packet,seqNumber,'sender'):

        print(f"DATA:\n\n {data.decode()}")
    else:
        print("[WRONG DATA !]")


client_socket.close()
    