# server
# Confiabilidade sobre o UDP tendo como base o rdt3.0
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

def not_corrupt (packet,seqNumber,type):

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
source_port = 12000
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('localhost', source_port))

print("[STARTING SERVER]...")
sleep(1)
print("[READY FOR CONNECTIONS]")

#Primeiro while responsavel por receber a conexao do cliente e enviar o ack do recebimento

while True:
    packet, address = server_socket.recvfrom(1024) #espera conexoes
    print(f"[CLIENT] - {address}")
    
    if not_corrupt(packet,seqNumber,'receiver'):# se a msg recebida pelo clientenao foi corrompida, manda o ack e att o seqnumber
       print("Dados recebidos sem problemas!!")
       server_socket.sendto(make_pkt(source_port,address[1],seqNumber,'ACK'),address)
       seqNumber = update_seq_number(seqNumber) 
    else:
        print("problema nos dados")
        server_socket.sendto(make_pkt(source_port,address[1],(1-seqNumber),'ACK'),address)
        
    msg = "      ----------CARDAPIO------------ \nNovo! Double Truffled Burger -- R$ 59,90\nAUSSIE PICANHA BURGER        -- R$ 49,90\nTHE OUTBACKER                -- R$ 44,90\nNED KELLY                    -- R$ 44,90\n" 
    #Esse while posterior sera responsavel por enviar a msg que o cliente pediu e esperar o ack do recebimento pelo cliente    
    ack = False
    server_socket.settimeout(1)

    while not ack:
        server_socket.sendto(make_pkt(source_port,address[1],seqNumber,msg), address) # enviando para o cliente
        server_socket.settimeout(1)#inicia o timer

        try:
            packet, address = server_socket.recvfrom(1024)
        
        except socket.timeout:
            print("ESTOURO DE TEMPO")
        
        else:
            ack = not_corrupt(packet,seqNumber,'sender')# verificar se o numero de seq ta certo e o checksum tambem

            seqNumber = update_seq_number(seqNumber)

    server_socket.settimeout(None)# desliga o timer

    
    
