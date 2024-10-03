import socket
import threading
import random
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

clients = []
number_to_guess = random.randint(1, 20)
max_attempts = 5
scores = {}
names = {}  # Armazenar nomes dos jogadores com base no endereço

def broadcast(message, sender_socket=None):
    for client_socket in clients:
        if client_socket != sender_socket:
            try:
                client_socket.sendall(message.encode('utf-8'))
            except:
                clients.remove(client_socket)

def reset_game():
    global number_to_guess
    number_to_guess = random.randint(1, 20)
    broadcast("Novo jogo iniciado! Tente adivinhar o número entre 1 e 20.\n")

def handle_client(client_socket, address):
    global number_to_guess
    try:
        attempts = 0
        names[address] = None
        scores[address] = 0
        logging.info(f"Cliente {address} conectado.")

        # Solicitar o nome do jogador
        client_socket.sendall("Digite seu nome:\n".encode('utf-8'))
        name = receive_message(client_socket)
        if name:
            names[address] = name
            broadcast(f"O jogador {name} entrou no jogo.\n")
        else:
            names[address] = f"Jogador {address}"

        welcome_message = f"Bem-vindo ao jogo de adivinhação, {names[address]}! Tente adivinhar o número entre 1 e 20. Você tem {max_attempts} tentativas.\n"
        client_socket.sendall(welcome_message.encode('utf-8'))

        while attempts < max_attempts:
            guess = receive_message(client_socket)
            if guess is None:
                break

            if guess.lower() == 'recomecar':
                reset_game()
                continue

            attempts += 1
            try:
                guess = int(guess)
                if guess < number_to_guess:
                    client_socket.sendall("Tente um número maior.\n".encode('utf-8'))
                elif guess > number_to_guess:
                    client_socket.sendall("Tente um número menor.\n".encode('utf-8'))
                else:
                    broadcast(f"Parabéns! O jogador {names[address]} adivinhou o número.\n")
                    scores[address] += 1
                    reset_game()
                    break
            except ValueError:
                client_socket.sendall("Por favor, insira um número válido.\n".encode('utf-8'))

        if attempts >= max_attempts:
            client_socket.sendall(f"Você excedeu o número máximo de tentativas. O número era {number_to_guess}.\n".encode('utf-8'))
    except Exception as e:
        logging.error(f"Erro com o cliente {address}: {e}")
    finally:
        clients.remove(client_socket)
        client_socket.close()
        logging.info(f"Conexão com o cliente {address} encerrada.")
        if address in scores:
            del scores[address]
        if address in names:
            del names[address]

def receive_message(client_socket):
    try:
        message = client_socket.recv(1024).decode('utf-8').strip()
        return message
    except:
        return None

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 9999))
    server.listen(5)
    logging.info("Servidor ouvindo na porta 9999")

    while True:
        client_socket, addr = server.accept()
        clients.append(client_socket)
        logging.info(f"Conexão aceita de {addr}")
        client_handler = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_handler.start()

if __name__ == "__main__":
    main()
