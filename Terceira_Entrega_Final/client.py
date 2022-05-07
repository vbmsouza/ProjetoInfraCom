# cliente
# Confiabilidade sobre o UDP tendo como base o rdt3.0
# Equipe 7 
# Alunos: Renan Guilherme Siqueira de Araújo, Flávio José Canuto de Vasconcelos Júnior, Vinícius Pereira de Araújo e 
#         Victor Bruno de Moura Souza. 
#funcao not_corrupt checa se os checksums sao iguais e se o num_de_sequencia tambem eh igual
#funcao makepkt cria pacote com num_de_seq, checksum, source_port,dest_port e os dados
#funcao update_seq_number atualiza o numero de sequencia
from datetime import date, datetime, time
from time import sleep
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
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
addr = ("127.0.0.1", 12000) 
source_port = 12000

print("{:02d}:{:02d}".format(datetime.now().hour,datetime.now().minute)+ " CINtofome: Digite sua mesa ")
mesa = input("{:02d}:{:02d}".format(datetime.now().hour,datetime.now().minute)+" Cliente: ")

print("{:02d}:{:02d}".format(datetime.now().hour,datetime.now().minute)+ " CINtofome: Digite seu nome ")
nome = input("{:02d}:{:02d}".format(datetime.now().hour,datetime.now().minute)+" Cliente: ")

msg = str(f"MESA {mesa}" + ',' + nome)

while 1:
    ack = False

    

    
    #segundo loop responsavel por enviar a msg do client e aguardar o ack, com o valor do ack sendo true, avançamos

    while not ack:
        client_socket.sendto(make_pkt(source_port,addr[1],seqNumber,msg), addr)
        client_socket.settimeout(1)#inicia o timer

        try:
            packet, server = client_socket.recvfrom(1024) # recebendo ack do client
        
        except socket.timeout:
            print("ESTOURO DE TEMPO")
        
        else:
            ack = not_corrupt(packet,seqNumber,'sender')# verificar se o numero de seq ta certo e o checksum tambem
            seqNumber = update_seq_number(seqNumber)#att o numero de seq apos o recebimen to do ack
 
    client_socket.settimeout(None)#desliga o timer
    # A partir daqui recebemos a msg do server
    packet, server = client_socket.recvfrom(1024) 
    data = packet[16:]
    

    if  not_corrupt(packet,seqNumber,'receiver'):
        if data.decode() == " Volte sempre ^^":
            print("{:02d}:{:02d}".format(datetime.now().hour,datetime.now().minute) + f" CINtofome:{data.decode()}")
            client_socket.sendto(make_pkt(source_port,server[1],seqNumber,'ACK'),server)
            
            sleep(3)
            client_socket.close()

        print("{:02d}:{:02d}".format(datetime.now().hour,datetime.now().minute) + f" CINtofome:{data.decode()}")
        client_socket.sendto(make_pkt(source_port,server[1],seqNumber,'ACK'),server)
        seqNumber = update_seq_number(seqNumber)
    else:
        print("[WRONG DATA !]")
        
        client_socket.sendto(make_pkt(source_port,server[1],(1-seqNumber),'ACK'),server)


    msg = str(input("{:02d}:{:02d}".format(datetime.now().hour,datetime.now().minute) + f" {nome}: "))
client_socket.close()
    