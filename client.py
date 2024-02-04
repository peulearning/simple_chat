import socket
import threading
import PySimpleGUI as sg
from datetime import datetime

sg.theme('DarkGrey5') # Seleciona Tema

class Client:
    def __init__(self, host, port, username):
        self.host = host
        self.port = port
        self.username = username
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Cria um socket IPv4 usando TCP
        self.gui_layout = [
            [sg.Multiline(size=(50, 10), key='-OUTPUT-', autoscroll=True)],
            [sg.InputText(key='-INPUT-', size=(50, 1)), sg.Button('Send')]
        ]
        self.window = sg.Window('Chat Client', self.gui_layout, finalize=True)  # Cria a interface gráfica

    def start_client(self):
        self.client_socket.connect((self.host, self.port))  # Conecta-se ao servidor
        self.client_socket.send(self.username.encode('utf-8'))  # Envia o nome de usuário ao servidor
        threading.Thread(target=self.receive_messages).start()  # Inicia uma thread para receber mensagens
        self.send_messages()  # Inicia o loop para enviar mensagens

    def send_messages(self):
        date_displayed = False

        while True:
            event, values = self.window.read()  # Lê eventos da interface gráfica

            if event == sg.WINDOW_CLOSED:
                exit_message = f"{self.username} saiu do chat."
                self.client_socket.send(exit_message.encode('utf-8'))  # Envia mensagem de saída ao servidor
                break

            if event == 'Send':
                message = values['-INPUT-']
                if not date_displayed:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self.window['-OUTPUT-'].print(f"Data: {timestamp}")  # Exibe a data no painel de saída
                    date_displayed = True

                formatted_message = f"{self.username}: {message}"
                self.client_socket.send(formatted_message.encode('utf-8'))  # Envia a mensagem formatada ao servidor
                self.window['-INPUT-'].update('')  # Limpa o campo de entrada após enviar a mensagem

        self.client_socket.close()  # Fecha o socket do cliente ao sair do loop

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')  # Recebe mensagens do servidor
                self.window['-OUTPUT-'].print(message)  # Exibe a mensagem no painel de saída
            except Exception as e:
                print(f"Error: {e}")
                break  # Sai do loop se houver um erro ao receber mensagens

if __name__ == "__main__":
    layout = [
        [sg.Text('Insira seu Nome:'), sg.InputText(key='-USERNAME-')],
        [sg.Button('Connect')]
    ]
    window = sg.Window('Chat BSI 1997', layout, finalize=True)  # Cria a interface gráfica inicial

    while True:
        event, values = window.read()  # Lê eventos da interface gráfica inicial

        if event == sg.WINDOW_CLOSED:
            break

        if event == 'Connect' and values['-USERNAME-']:
            window.close()  # Fecha a interface gráfica inicial
            client = Client('localhost', 5555, values['-USERNAME-'])  # Cria uma instância do cliente
            client.start_client()  # Inicia o cliente
            break  # Sai do loop após a conexão ser estabelecida
