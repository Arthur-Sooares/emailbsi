import socket
import threading
import bcrypt
import time

HOST = '127.0.0.1'
PORTA = 65432

# Dicionário para armazenar usuários (username: hash_senha)
usuarios = {}

# Lista para armazenar e-mails temporariamente (destinatario: [emails])
emails = {}

# Lock para proteger o acesso a dados compartilhados (usuarios, emails)
lock = threading.Lock()


def gerar_log(mensagem):
    """Gera uma mensagem de log com timestamp."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {mensagem}")


def lidar_com_cliente(conexao, endereco):
    """Lida com a conexão de um cliente."""
    print(f"Conectado por {endereco}")

    try:
        while True:
            data = conexao.recv(1024).decode()
            if not data:
                break

            partes = data.split(":", 1)
            comando = partes[0]
            payload = partes[1] if len(partes) > 1 else ""

            if comando == "CADASTRO":
                nome_completo, username, senha = payload.split(":")
                with lock:
                    if username in usuarios:
                        conexao.sendall("ERRO: Usuario ja existe".encode())
                    else:
                        senha_criptografada = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())
                        usuarios[username] = senha_criptografada
                        gerar_log(f"Novo usuario cadastrado: {username}")
                        conexao.sendall("SUCESSO: Cadastro realizado".encode())

            elif comando == "LOGIN":
                username, senha = payload.split(":")
                with lock:
                    if username in usuarios:
                        senha_criptografada = usuarios[username]
                        if bcrypt.checkpw(senha.encode('utf-8'), senha_criptografada):
                            gerar_log(f"Usuario {username} autenticado")
                            conexao.sendall("SUCESSO: Login realizado".encode())
                        else:
                            conexao.sendall("ERRO: Senha incorreta".encode())
                    else:
                        conexao.sendall("ERRO: Usuario nao existe".encode())

            elif comando == "ENVIAR_EMAIL":
                remetente, destinatario, assunto, corpo = payload.split(":", 3)
                with lock:
                    if destinatario in usuarios:
                        if destinatario not in emails:
                            emails[destinatario] = []
                        emails[destinatario].append({
                            "remetente": remetente,
                            "assunto": assunto,
                            "corpo": corpo
                        })
                        gerar_log(f"Email de {remetente} para {destinatario}")
                        conexao.sendall("SUCESSO: E-mail enviado".encode())
                    else:
                        conexao.sendall("ERRO: Destinatario inexistente".encode())

            elif comando == "RECEBER_EMAILS":
                username = payload
                with lock:
                    if username in emails:
                        lista_emails = emails[username]
                        resposta = "SUCESSO:"
                        for i, email in enumerate(lista_emails):
                            resposta += f"{i + 1}. De: {email['remetente']}, Assunto: {email['assunto']};"

                        del emails[username]  # Remove os emails depois de enviados para o cliente
                        conexao.sendall(resposta.encode())
                    else:
                        conexao.sendall("SUCESSO: Voce nao tem emails".encode())


            else:
                conexao.sendall("ERRO: Comando invalido".encode())


    except Exception as e:
        print(f"Erro na conexão: {e}")
    finally:
        print(f"Conexão com {endereco} encerrada")
        conexao.close()


def main():
    """Função principal do servidor."""
    servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor_socket.bind((HOST, PORTA))
    servidor_socket.listen()

    print(f"Servidor escutando em {HOST}:{PORTA}")

    try:
        while True:
            conexao, endereco = servidor_socket.accept()
            thread = threading.Thread(target=lidar_com_cliente, args=(conexao, endereco))
            thread.start()
    except KeyboardInterrupt:
        print("Servidor encerrado.")
    finally:
        servidor_socket.close()


if __name__ == "__main__":
    main()