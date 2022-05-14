import tkinter as tk
from threading import Thread
from socket import *
import requests

headers ={
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36 OPR/40.0.2308.81',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'DNT': '1',
    'Accept-Encoding': 'gzip, deflate, lzma, sdch',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4'
}

DEFAULT_SOURCE_HOST = '127.0.0.1'
DEFAULT_SOURCE_PORT = 1000
DEFAULT_DEST_PORT = 80

stop_threads = False


class RuleSocket:
    def __init__(self, source_host, source_port, dest_host, dest_port):
        self.url = f'http://{dest_host}:{dest_port}'
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.bind((source_host, source_port))
        self.socket.listen(1)

    def run(self):
        global stop_threads

        while True:
            client_socket, _ = self.socket.accept()
            client_socket.recv(1024)
            response = requests.get(self.url, headers=headers)
            response = response.content.decode(response.encoding or 'utf-8')
            client_socket.send(bytes(f'HTTP/1.1 200 OK\r\nContent-Length: {len(response)}\r\n\r\n{response}', 'utf-8'))
            client_socket.close()
            if stop_threads:
                break


class TranslationRule:
    def __init__(self, ind, source_host, source_port, dest_host, dest_port):
        self.socket = None
        self.ind = ind
        self.source_host = source_host
        self.source_port = int(source_port)
        self.dest_host = dest_host
        self.dest_port = int(dest_port)
        self.on = False

    def apply(self):
        self.socket = RuleSocket(self.source_host, self.source_port, self.dest_host, self.dest_port)
        self.on = True


def add_rule():
    rules.append(TranslationRule(len(rules), e_src_host.get(), e_src_port.get(), e_dest_host.get(), e_dest_port.get()))
    if len(rules) == 1:
        msg = tk.Message(master, text='Список правил:', width=200)
        msg.config(font=24, fg='red')
        msg.grid(row=2)
        tk.Label(master, text='Внутренний IP').grid(row=3, column=0)
        tk.Label(master, text='Внутренний порт').grid(row=3, column=1)
        tk.Label(master, text='Внешний IP').grid(row=3, column=2)
        tk.Label(master, text='Внешний порт').grid(row=3, column=3)
    i = len(rules) + 3
    tk.Label(master, text=e_src_host.get()).grid(row=i, column=0)
    tk.Label(master, text=e_src_port.get()).grid(row=i, column=1)
    tk.Label(master, text=e_dest_host.get()).grid(row=i, column=2)
    tk.Label(master, text=e_dest_port.get()).grid(row=i, column=3)

    e_src_host.delete(0, tk.END)
    e_src_host.insert(10, DEFAULT_SOURCE_HOST)
    e_src_port.delete(0, tk.END)
    e_src_port.insert(10, str(DEFAULT_SOURCE_PORT + len(rules)))
    e_dest_host.delete(0, tk.END)
    e_dest_port.delete(0, tk.END)
    e_dest_port.insert(10, str(DEFAULT_DEST_PORT))


def run_translator():
    for rule in rules:
        if rule.on:
            continue
        rule.apply()
        threads.append(Thread(target=lambda: rule.socket.run()))
        threads[-1].start()


def close():
    global stop_threads

    for thread in threads:
        stop_threads = True
        thread.join()
    master.destroy()


master = tk.Tk()
master.title('Port Translator')
tk.Label(master, text='Внутренний IP').grid(row=0, column=0)
tk.Label(master, text='Внутренний порт').grid(row=0, column=1)
tk.Label(master, text='Внешний IP').grid(row=0, column=2)
tk.Label(master, text='Внешний порт').grid(row=0, column=3)

add_rule_bt = tk.Button(master,
                        text='Добавить правило',
                        width=20,
                        command=add_rule)
run_translator_bt = tk.Button(master,
                              text='Запустить транслятор',
                              width=20,
                              command=run_translator)
close_bt = tk.Button(master,
                    text='Выйти',
                    width=20,
                    command=close)
add_rule_bt.grid(row=0, column=5, padx=5)
run_translator_bt.grid(row=1, column=5, padx=5)
close_bt.grid(row=2, column=5, padx=5)

e_src_host = tk.Entry(master)
e_src_port = tk.Entry(master)
e_dest_host = tk.Entry(master)
e_dest_port = tk.Entry(master)
e_src_host.insert(10, DEFAULT_SOURCE_HOST)
e_src_port.insert(10, str(DEFAULT_SOURCE_PORT))
e_dest_host.insert(10, '')
e_dest_port.insert(10, str(DEFAULT_DEST_PORT))

e_src_host.grid(row=1, column=0)
e_src_port.grid(row=1, column=1)
e_dest_host.grid(row=1, column=2)
e_dest_port.grid(row=1, column=3)

rules = []
threads = []

master.mainloop()
