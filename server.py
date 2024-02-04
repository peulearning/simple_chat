import socket
import threading
from queue import Queue
from datetime import datetime
import os

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = []
        self.message_queue = Queue()
        self.server_running = True
        self.start_server()

    def start_server(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()

        print(f"Server listening on {self.host}:{self.port}")

        threading.Thread(target=self.send_messages_to_clients).start()
        threading.Thread(target=self.await_enter_key).start()

        while self.server_running:
            client_socket, client_address = self.server_socket.accept()
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_thread.start()
            self.clients.append(client_socket)

    def handle_client(self, client_socket):
        try:
            username = client_socket.recv(1024).decode('utf-8')
            entry_message = f"{username} entrou no chat."
            self.message_queue.put(entry_message)

            date_displayed = False

            while True:
                message = client_socket.recv(1024).decode('utf-8')
                if not message:
                    break

                if not date_displayed:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self.message_queue.put(f"Data: {timestamp}")
                    date_displayed = True

                formatted_message = f"{message}"
                self.message_queue.put(formatted_message)

            exit_message = f"{username} saiu do chat."
            self.message_queue.put(exit_message)

        except Exception as e:
            print(f"Error: {e}")

    def send_messages_to_clients(self):
        while self.server_running:
            if not self.message_queue.empty():
                message = self.message_queue.get()
                for client_socket in self.clients:
                    try:
                        client_socket.send(message.encode('utf-8'))
                    except Exception as e:
                        print(f"Error: {e}")
                        self.clients.remove(client_socket)

    def await_enter_key(self):
        input("Press [ ENTER ] to close server ... ")
        self.server_running = False
        self.server_socket.close()
        print("Server closed.")
        os._exit(0)  # Encerra o programa

if __name__ == "__main__":
    server = Server('localhost', 5555)
