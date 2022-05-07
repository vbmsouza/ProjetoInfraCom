# server
# Confiabilidade sobre o UDP tendo como base o rdt3.0
# Equipe 7 
# Alunos: Renan Guilherme Siqueira de Araújo, Flávio José Canuto de Vasconcelos Júnior, Vinícius Pereira de Araújo e 
#         Victor Bruno de Moura Souza. 
from datetime import datetime
import msvcrt
from multiprocessing.sharedctypes import Value
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


def pedido_e_preco(pedido):
    if pedido == "7" or pedido =="lasanha":
        return ("Lasanha",44.9)
    elif pedido == "8" or pedido =="batata frita":
        return ("Batata Frita",9.9)
    elif pedido == "9" or pedido =="frango a parmegiana":
        return ("Frango a Parmegiana",59.9)
    elif pedido == "10" or pedido =="strogonoff":
        return ("Strogonoff",44.9)
    else:
        return 0


def att_conta(dic, pedidos, mesa,nome):
    for pedido in pedidos:
        pedido,preco = pedido_e_preco(pedido)
        dic[mesa][nome][pedido] = preco

def conta_individual_total(dic,mesa,nome):
    conta = 0
    for value in dic[mesa][nome].values():
        conta = conta + value
    return conta

def print_conta_individual(dic,mesa,nome):
    msg = ''
    for keys,values in dic[mesa][nome].items():
        msg = msg + ("\n{} => R$ {}".format(keys,values))
    return (f"\n------------| {nome} |-----------\n" + msg + "\n-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-"+ f"\n\nTotal - R$ {conta_individual_total(dic,mesa,nome)}\n")

def conta_total(dic,mesa):
    conta = 0
    for values in dic[mesa]:
        conta = conta + conta_individual_total(dic,mesa,values)

    return conta

def print_conta_total(dic,mesa):
    msg=''
    for values in dic[mesa]:
        msg = msg + print_conta_individual(dic,mesa,values) 
    return (msg + f"\n\nTotal da Mesa - R$ {conta_total(dic,mesa)}\n")

def pagar(dic,mesa,nome,valor):
    if valor < conta_individual_total(dic,mesa,nome):
        msg = "Valor abaixo do esperado. Digite outro valor"
        return msg
    elif valor > conta_individual_total(dic,mesa,nome) and valor < conta_total(dic,mesa):
        excendente = conta_total(dic,mesa) - conta_individual_total(dic,mesa,nome)
        msg = f"Você está pagando R$ {excendente} a mais que sua conta. O valor excedente será distribuído para os outros clientes.(digite sim para para confirmar)"
        return msg
        
    elif valor == conta_individual_total(dic,mesa,nome):
        msg = "Você pagou sua conta, obrigado!"
        dic[mesa][nome] = {}
        return msg
    else:
        msg = "Você esta pagando uma quantia maior ou igual que o valor da mesa, o excedente será doado para ONGs.(digite doar para confirmar)"
        return msg

def menu_decision(msg,dic,mesa,nome,connecteds,address):
    try :
        msg = float(msg)
        msg = pagar(dic,mesa,nome,msg)

    except:
        if msg =="c" or msg =="cardapio":
            msg = "\n      ----------CARDAPIO------------ \n7. LASANHA -- R$ 44,90\n8. BATATA FRITA        -- R$ 9,90\n9. FRANGO A PARMEGIANA                -- R$ 59,90\n10. STROGONOFF                    -- R$ 44,90\n" 
        
        elif msg =="pedir" or msg =="p":
            msg = "Digite os pedidos separados por ponto e virgula (número ou por extenso):"
        
        elif  msg == "m" or msg =="voltar":
            msg = "\n           ---------CINtoFOME----------- \nc - cardápio\np - pedir\nci - conta individual\ncm - conta da mesa\ne - pagar\nl. levantar\nm. CinToFome\n"
        
        elif msg =="i" or msg == "conta individual":
            msg = "\n------------CONTA INDIVIDUAL---------\n" + print_conta_individual(dic,mesa,nome)
        
        elif msg =='m' or msg == 'conta da mesa':
            msg = "\n------------CONTA DA MESA-----------\n" + print_conta_total(restaurante,mesa)
        
        elif msg == "e"or msg =="pagar":
            msg = f" Sua conta foi R$ {conta_individual_total(dic,mesa,nome)} e a da mesa R$ {conta_total(dic,mesa)}. Digite o valor a ser pago"
        
        elif msg == "sim":
            dic[mesa][nome]={}
        
        elif msg == "doar":
            for values in dic[mesa]:
                dic[mesa][values] = {}
        
        elif msg == 'levantar':
            if dic[mesa][nome] == {}:
                del dic[mesa][nome]
                del connecteds[address]
                msg = " Volte sempre ^^"

            else:
                msg = " Você ainda não pagou sua conta"
        else:
            pedidos = msg.lower().split(';')
            msg = "Iremos preparar o seu pedido"
            att_conta(dic,pedidos,mesa,nome)
    
    return msg

seqNumber = 0        
source_port = 12000
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('localhost', source_port))

print("[STARTING SERVER]...")
sleep(1)
print("[READY FOR CONNECTIONS]")
restaurante = {}
#Primeiro while responsavel por receber a conexao do cliente e enviar o ack do recebimento
connecteds = {}
while True:
    packet, address = server_socket.recvfrom(1024) #espera conexoes
    if address not in connecteds:
        connecteds[address] = {}
    
    if not_corrupt(packet,seqNumber,'receiver'):# se a msg recebida pelo clientenao foi corrompida, manda o ack e att o seqnumber
        server_socket.sendto(make_pkt(source_port,address[1],seqNumber,'ACK'),address)
        seqNumber = update_seq_number(seqNumber)
        try:
            msg = packet[16:].decode()
            mesa,nome = msg.split(',')
            connecteds[address]['user'] = nome
            connecteds[address]['table'] = mesa
            
            if mesa in restaurante:
        
                restaurante[mesa][nome] = {}
            else:
                restaurante[mesa] = {nome:{}}
                msg = "\n           ---------CINtoFOME----------- \nc - cardápio\np - pedir\ni - conta individual\nm - conta da mesa\ne - pagar\nl. levantar\nm. CinToFome\n"

        except:
            msg = packet[16:].decode()
            msg = menu_decision(msg,restaurante,mesa,nome,connecteds,address)
            
       
    else:
        print("problema nos dados")
        server_socket.sendto(make_pkt(source_port,address[1],(1-seqNumber),'ACK'),address)

    print(restaurante)
    
    #msg = "           ---------CINtoFOME----------- \n1 - cardápio\n2 - pedido\n3 - conta individual\n4 - não fecho com robô, chame seu gerente\n5 - nada não, tava só testando\n6 - conta da mesa"
    #msg = "      ----------CARDAPIO------------ \nNovo! Double Truffled Burger -- R$ 59,90\nAUSSIE PICANHA BURGER        -- R$ 49,90\nTHE OUTBACKER                -- R$ 44,90\nNED KELLY                    -- R$ 44,90\n" 
    #Esse while posterior sera responsavel por enviar a msg que o cliente pediu e esperar o ack do recebimento pelo cliente    
   
    ack = False

    while not ack:
        server_socket.sendto(make_pkt(source_port,address[1],seqNumber,str(msg)), address) # enviando para o cliente
        server_socket.settimeout(1)#inicia o timer

        try:
            packet, address = server_socket.recvfrom(1024)
        
        except socket.timeout:
            print("ESTOURO DE TEMPO")
        
        else:
            ack = not_corrupt(packet,seqNumber,'sender')# verificar se o numero de seq ta certo e o checksum tambem

            seqNumber = update_seq_number(seqNumber)

    server_socket.settimeout(None)# desliga o timer
    print(connecteds)
        
