# server
# Confiabilidade sobre o UDP tendo como base o rdt3.0
# Equipe 7 
# Alunos: Renan Guilherme Siqueira de Araújo, Flávio José Canuto de Vasconcelos Júnior, Vinícius Pereira de Araújo e 
#         Victor Bruno de Moura Souza. 
from datetime import datetime
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

def not_corrupt (packet,seqNumber,type):#checa se está corrompido

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

#A funcao abaixo é responsavel por converter o pedido em uma tupla com nome do pedido e o preço
def pedido_e_preco(pedido):
    if pedido == "x" or pedido =="lasanha":
        return ("Lasanha",44.9)
    elif pedido == "y" or pedido =="batata frita":
        return ("Batata Frita",9.9)
    elif pedido == "z" or pedido =="frango a parmegiana":
        return ("Frango a Parmegiana",59.9)
    elif pedido == "w" or pedido =="strogonoff":
        return ("Strogonoff",44.9)
    else:
        return 0

#A funcao abaixo é responsavel por atualizar a conta do cliente,
# colocando os pedidos e seu preço na na estrutura de dados que tem cliente, biblioteca nesse caso.
def att_conta(dic, pedidos, mesa,nome):
    for pedido in pedidos:
        pedido,preco = pedido_e_preco(pedido)
        dic[mesa][nome][pedido] = preco

#A funcao abaixo calcula o total da conta de um cliente
def conta_individual_total(dic,mesa,nome):
    conta = 0
    for value in dic[mesa][nome].values():
        conta = conta + value
    return float(conta)

#A funcao abaixo printa uma especie de nota fiscal com a conta individual do cliente e seu total
def print_conta_individual(dic,mesa,nome):
    msg = ''
    for keys,values in dic[mesa][nome].items():
        msg = msg + ("\n{} => R$ {}".format(keys,values))
    return (f"\n------------| {nome} |-----------\n" + msg + "\n-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-"+ f"\n\nTotal - R$ {conta_individual_total(dic,mesa,nome)}\n")

#A funcao abaixo retorna a conta total da mesa
def conta_total(dic,mesa):
    conta = 0
    for values in dic[mesa]:
        conta = conta + conta_individual_total(dic,mesa,values)

    return float(conta)

#A funcao abaixo retorna uma nota fiscal com a conta da mesa, estando presente as contas individuais de cada um da mesa.
def print_conta_total(dic,mesa):
    msg=''
    for values in dic[mesa]:
        msg = msg + print_conta_individual(dic,mesa,values) 
    return (msg + f"\n\nTotal da Mesa - R$ {conta_total(dic,mesa)}\n")


#A funcao abaixo retorna uma msg para os 3 tipos de pagamento: 1. pagamento menor do que a conta individual.
#                                                              2. pagamento maior do que a conta individual.
#                                                              3. pagamento maior ou igual ao valor total da mesa.
def pagar(dic,mesa,nome,valor):
    if valor < conta_individual_total(dic,mesa,nome):
        msg = "Valor abaixo do esperado. Digite outro valor"
        return msg
    elif valor > conta_individual_total(dic,mesa,nome) and valor < conta_total(dic,mesa):
        excendente = valor - conta_individual_total(dic,mesa,nome)
        msg = f"Você está pagando R$ {excendente} a mais que sua conta. O valor excedente será distribuído para os outros clientes.(digite sim para para confirmar)"
        return msg
        
    elif valor == conta_individual_total(dic,mesa,nome):
        msg = "Você pagou sua conta, obrigado!"
        dic[mesa][nome] = {}
        return msg
    else:
        msg = "Você esta pagando uma quantia maior ou igual que o valor da mesa, o excedente será doado para ONGs.(digite doar para confirmar)"
        return msg

#A funcao abaixo é o menu, caso seja um numero ele ira saber que o cliente esta querendo pagar,
# caso contrario aciona as outras funcoes. 
def menu_decision(msg,dic,mesa,nome):
    try :
        msg = float(msg)
        msg = pagar(dic,mesa,nome,msg)

    except:
        if msg =="c" or msg =="cardapio":
            msg = "\n      ----------CARDAPIO------------ \nx. LASANHA -- R$ 44,90\ny. BATATA FRITA        -- R$ 9,90\nz. FRANGO A PARMEGIANA                -- R$ 59,90\nw. STROGONOFF                    -- R$ 44,90\n" 
        
        elif msg =="pedir" or msg =="p":
            msg = "Digite os pedidos separados por ponto e virgula (letra ou por extenso):"
        
        elif  msg == "-" or msg =="voltar":
            msg = "\n           ---------CINtoFOME----------- \nc - cardápio\np - pedir\ni - conta individual\nm - conta da mesa\ne - pagar\nl. levantar\n-. CinToFome\n"
        
        elif msg =="i" or msg == "conta individual":
            msg = "\n------------CONTA INDIVIDUAL---------\n" + print_conta_individual(dic,mesa,nome)
        
        elif msg =='m' or msg == 'conta da mesa':
            msg = "\n------------CONTA DA MESA-----------\n" + print_conta_total(dic,mesa)
        
        elif msg == "e"or msg =="pagar":
            msg = f" Sua conta foi R$ {conta_individual_total(dic,mesa,nome)} e a da mesa R$ {conta_total(dic,mesa)}. Digite o valor a ser pago"
        
        elif msg == "sim":
            dic[mesa][nome]={}
        
        elif msg == "doar":
            for values in dic[mesa]:
                dic[mesa][values] = {}
            msg = "valor excedente doado"
        elif msg == 'levantar' or msg=="l":
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

#Criando o server,porta e ip
seqNumber = 0        
source_port = 12000
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('localhost', source_port))

print("[STARTING SERVER]...")
sleep(1)
print("[READY FOR CONNECTIONS]")
restaurante = {}
connecteds = {}
#Primeiro while responsavel por receber a conexao do cliente e enviar o ack do recebimento

while True:
    packet, address = server_socket.recvfrom(1024) #espera conexoes
    if address not in connecteds:
        connecteds[address] = {}
    
    if not_corrupt(packet,seqNumber,'receiver'):# se a msg recebida pelo clientenao foi corrompida, manda o ack e att o seqnumber
        server_socket.sendto(make_pkt(source_port,address[1],seqNumber,'ACK'),address)
        seqNumber = update_seq_number(seqNumber)
        # try abaixo responsavel por saber se o tipo de msg enviada é a de cadastro,
        #   caso contrario ele vai para o menu de decisao
        try:
            msg = packet[16:].decode()
            mesa,nome = msg.split(',')
            connecteds[address]['user'] = nome
            connecteds[address]['table'] = mesa
            
            if mesa in restaurante:
        
                restaurante[mesa][nome] = {}
            else:
                restaurante[mesa] = {nome:{}}
            msg = "\n           ---------CINtoFOME----------- \nc - cardápio\np - pedir\ni - conta individual\nm - conta da mesa\ne - pagar\nl. levantar\n-. CinToFome\n"

        except:
            msg = packet[16:].decode()
            msg = menu_decision(msg,restaurante,connecteds[address]['table'],connecteds[address]['user'])
            
       
    else:
        print("problema nos dados")
        server_socket.sendto(make_pkt(source_port,address[1],(1-seqNumber),'ACK'),address)

    print(f"restaurante = {restaurante}")
    
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
    print(f"conectados = {connecteds}\n")
