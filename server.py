import socket
import threading
from queue import Queue
from datetime import datetime
import os

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Cria um socket IPv4 usando TCP
        self.clients = []  # Lista para armazenar os sockets dos clientes conectados
        self.message_queue = Queue()  # Fila para armazenar mensagens a serem enviadas aos clientes
        self.server_running = True  # Flag para indicar se o servidor está em execução
        self.start_server()  # Inicia o servidor

    def start_server(self):
        self.server_socket.bind((self.host, self.port))  # Associa o socket ao endereço e porta especificados
        self.server_socket.listen()  # Coloca o socket em modo de escuta para aceitar conexões

        print(f"Server listening on {self.host}:{self.port}")

        # Inicia duas threads secundárias para lidar com o envio de mensagens aos clientes e aguardar a tecla Enter
        threading.Thread(target=self.send_messages_to_clients).start()
        threading.Thread(target=self.await_enter_key).start()

        while self.server_running:
            # Aceita a conexão de um cliente e cria uma nova thread para lidar com esse cliente
            client_socket, client_address = self.server_socket.accept()
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_thread.start()
            self.clients.append(client_socket)

    def handle_client(self, client_socket):
        try:
            username = client_socket.recv(1024).decode('utf-8')  # Recebe o nome de usuário do cliente
            entry_message = f"{username} entrou no chat."
            self.message_queue.put(entry_message)  # Adiciona a mensagem de entrada à fila

            date_displayed = False

            while True:
                message = client_socket.recv(1024).decode('utf-8')  # Recebe a mensagem do cliente
                if not message:
                    break

                # Exibe a data apenas uma vez quando o cliente começa a enviar mensagens
                if not date_displayed:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self.message_queue.put(f"Data: {timestamp}")
                    date_displayed = True

                formatted_message = f"{message}"
                self.message_queue.put(formatted_message)  # Adiciona a mensagem formatada à fila

            exit_message = f"{username} saiu do chat."
            self.message_queue.put(exit_message)  # Adiciona a mensagem de saída à fila

        except Exception as e:
            print(f"Error: {e}")

    def send_messages_to_clients(self):
        while self.server_running:
            if not self.message_queue.empty():
                message = self.message_queue.get()  # Obtém a mensagem da fila
                # Envia a mensagem para todos os clientes conectados
                for client_socket in self.clients:
                    try:
                        client_socket.send(message.encode('utf-8'))
                    except Exception as e:
                        print(f"Error: {e}")
                        self.clients.remove(client_socket)  # Remove o cliente se houver um erro ao enviar a mensagem

    def await_enter_key(self):
        input("Press [ ENTER ] to close server ... ")  # Aguarda a entrada da tecla Enter
        self.server_running = False  # Sinaliza para encerrar o servidor
        self.server_socket.close()  # Fecha o socket do servidor
        print("Server closed.")
        os._exit(0)  # Encerra o programa

if __name__ == "__main__":
    server = Server('localhost', 5555)  # Cria uma instância do servidor
