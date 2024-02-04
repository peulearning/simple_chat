import socket
import threading
import PySimpleGUI as sg
from datetime import datetime

sg.theme('DarkGrey5')

class Client:
    def __init__(self, host, port, username):
        self.host = host
        self.port = port
        self.username = username
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.gui_layout = [
            [sg.Multiline(size=(50, 10), key='-OUTPUT-', autoscroll=True)],
            [sg.InputText(key='-INPUT-', size=(50, 1)), sg.Button('Send')]
        ]
        self.window = sg.Window('Chat Client', self.gui_layout, finalize=True)

    def start_client(self):
        self.client_socket.connect((self.host, self.port))
        self.client_socket.send(self.username.encode('utf-8'))
        threading.Thread(target=self.receive_messages).start()
        self.send_messages()

    def send_messages(self):
        date_displayed = False

        while True:
            event, values = self.window.read()

            if event == sg.WINDOW_CLOSED:
                exit_message = f"{self.username} saiu do chat."
                self.client_socket.send(exit_message.encode('utf-8'))
                break

            if event == 'Send':
                message = values['-INPUT-']
                if not date_displayed:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self.window['-OUTPUT-'].print(f"Data: {timestamp}")
                    date_displayed = True

                formatted_message = f"{self.username}: {message}"
                self.client_socket.send(formatted_message.encode('utf-8'))
                self.window['-INPUT-'].update('')

        self.client_socket.close()

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                self.window['-OUTPUT-'].print(message)
            except Exception as e:
                print(f"Error: {e}")
                break

if __name__ == "__main__":
    layout = [
        [sg.Text('Insira seu Nome:'), sg.InputText(key='-USERNAME-')],
        [sg.Button('Connect')]
    ]
    window = sg.Window('Chat BSI 1997', layout, finalize=True)

    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED:
            break

        if event == 'Connect' and values['-USERNAME-']:
            window.close()
            client = Client('localhost', 5555, values['-USERNAME-'])
            client.start_client()
            break
