# app.py
import socket
import threading
import time

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Static, Header, Footer, Input, Log, ListView, ListItem



class ClientConnection:
    def __init__(self, conn, addr):
        self.conn = conn
        self.addr = addr
        self.log_file = open(f"{addr[0]}_{addr[1]}.txt", "ab")
        self.thread = None

class ShellApp(App):
    CSS_PATH = "styles.tcss"

    def __init__(self):
        super().__init__()
        self.clients: list[ClientConnection] = []
        self.active_client: ClientConnection | None = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            yield ListView(id="client_list")
            with Vertical():
                yield Log(id="shell_log")
                yield Input(placeholder="Type command here...", id="cmd_input")
        yield Footer()

    async def on_mount(self):
        
        threading.Thread(target=self.listen_for_clients, daemon=True).start()

    def listen_for_clients(self):
        host = "0.0.0.0"
        port = 5678
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen(5)

        while True:
            conn, addr = s.accept()
            client = ClientConnection(conn, addr)
            self.clients.append(client)
            self.call_from_thread(self.add_client_to_ui, client)
            threading.Thread(target=self.receive_output, args=(client,), daemon=True).start()

    def add_client_to_ui(self, client: ClientConnection):
        label = f"{client.addr[0]}:{client.addr[1]}"
        self.query_one("#client_list", ListView).append(ListItem(Static(label)))

    def receive_output(self, client: ClientConnection):
        while True:
            try:
                data = client.conn.recv(6048)
                if not data:
                    raise ConnectionError
                if client == self.active_client:
                    self.call_from_thread(
                        lambda: self.query_one("#shell_log", Log).write(data.decode(errors="ignore"))
                    )
                    client.log_file.write(data)
                    client.log_file.write(b"\n")
                    client.log_file.flush()
            except:
                client.conn.close()
                client.log_file.close() 
                break

    async def on_list_view_selected(self, event: ListView.Selected):
        selected_index = event.index
        self.active_client = self.clients[selected_index]
        self.query_one("#shell_log", Log).clear()
        self.query_one("#shell_log", Log).write(f"Connected to {self.active_client.addr[0]}...\n")

    async def on_input_submitted(self, event: Input.Submitted):
        if not self.active_client:
            return
        cmd = event.value.strip() + "\n"
        try:
            self.active_client.conn.send(cmd.encode())
            self.query_one("#cmd_input", Input).value = ""
        except:
            self.query_one("#shell_log", Log).write("[ERROR] Failed to send command.\n")

if __name__ == "__main__":
    ShellApp().run()
