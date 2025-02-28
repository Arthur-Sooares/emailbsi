import socket

HOST = '127.0.0.1'  
PORTA = 65432  


def mostrar_menu_principal():
    """Mostra o menu principal do cliente."""
    print("\nCliente E-mail Service BSI Online")
    print("1) Apontar Servidor")
    print("2) Cadastrar Conta")
    print("3) Acessar E-mail")
    print("0) Sair")


def apontar_servidor():
    """Permite ao usuario configurar o endereco do servidor."""
    global HOST, PORTA
    HOST = input("Digite o IP do servidor (padrao: 127.0.0.1): ") or HOST
    PORTA = int(input("Digite a porta do servidor (padrao: 65432): ") or PORTA)

    try:
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_cliente:
            socket_cliente.settimeout(2)  
            socket_cliente.connect((HOST, PORTA))
            print("Servico Disponivel")
            return True
    except:
        print("Servico Indisponivel. Verifique o IP e a porta.")
        return False


def cadastrar_conta(socket_cliente):
    """Permite ao usuario cadastrar uma nova conta."""
    nome_completo = input("Digite seu nome completo: ")
    username = input("Digite um username (sem espaços): ")
    senha = input("Digite sua senha: ")

    mensagem = f"CADASTRO:{nome_completo}:{username}:{senha}"
    socket_cliente.sendall(mensagem.encode())

    data = socket_cliente.recv(1024).decode()
    print(data)  


def acessar_email(socket_cliente):
    """Permite ao usuario acessar sua conta de email."""
    username = input("Digite seu username: ")
    senha = input("Digite sua senha: ")

    mensagem = f"LOGIN:{username}:{senha}"
    socket_cliente.sendall(mensagem.encode())

    data = socket_cliente.recv(1024).decode()
    if "SUCESSO" in data:
        print("Login realizado com sucesso!")
        tela_boas_vindas(socket_cliente, username)
    else:
        print(data)  


def tela_boas_vindas(socket_cliente, username):
    """Mostra a tela de boas vindas e o menu de e-mail."""
    print(f"\nSeja Bem Vindo(a) {username}!")
    while True:
        print("\n4) Enviar E-mail")
        print("5) Receber E-mails")
        print("6) Logout")

        opcao = input("Escolha uma opcao: ")

        if opcao == "4":
            enviar_email(socket_cliente, username)
        elif opcao == "5":
            receber_emails(socket_cliente, username)
        elif opcao == "6":
            print("Logout realizado.")
            break
        else:
            print("Opcao invalida.")


def enviar_email(socket_cliente, remetente):
    """Permite ao usuario enviar um e-mail."""
    destinatario = input("Digite o username do destinatario: ")
    assunto = input("Digite o assunto: ")
    corpo = input("Digite o corpo do e-mail: ")

    mensagem = f"ENVIAR_EMAIL:{remetente}:{destinatario}:{assunto}:{corpo}"
    socket_cliente.sendall(mensagem.encode())

    data = socket_cliente.recv(1024).decode()
    print(data)


def receber_emails(socket_cliente, username):
    """Permite ao usuario receber seus e-mails."""
    mensagem = f"RECEBER_EMAILS:{username}"
    socket_cliente.sendall(mensagem.encode())

    data = socket_cliente.recv(2048).decode()  
    if "SUCESSO:" in data:
        emails = data[8:].split(";")  
        if emails[0] == '':
            print('Voce nao tem novos e-mails!')
            return
        print("Seus e-mails:")
        for email in emails[:-1]: 
            print(email)

    else:
        print(data)


def main():
    """Funcao principal do cliente."""
    servidor_apontado = False
    while True:
        mostrar_menu_principal()
        opcao = input("Escolha uma opcao: ")

        if opcao == "1":
            servidor_apontado = apontar_servidor()
        elif opcao == "2":
            if servidor_apontado:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_cliente:
                    socket_cliente.connect((HOST, PORTA))
                    cadastrar_conta(socket_cliente)
            else:
                print("Por favor, aponte o servidor primeiro.")
        elif opcao == "3":
            if servidor_apontado:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_cliente:
                    socket_cliente.connect((HOST, PORTA))
                    acessar_email(socket_cliente)
            else:
                print("Por favor, aponte o servidor primeiro.")
        elif opcao == "0":
            print("Encerrando o cliente.")
            break
        else:
            print("Opcao invalida.")


if __name__ == "__main__":
    main()
