import socket
import threading
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk

class GuessingGameClient:
    def __init__(self, master):
        self.master = master
        self.master.title("Jogo de Adivinhação")
        self.master.geometry("800x600")
        self.master.resizable(True, True)

        # Configuração de estilos
        self.style = ttk.Style()
        self.style.configure("TFrame", background="#006eb3")  # Cor de fundo mais escura
        self.style.configure("TLabel", background="#006eb3", font=("Helvetica", 12), foreground="#ffffff")  # Texto em branco

        # Estilo para o botão "OK"
        self.style.configure("OKButton.TButton", font=("Helvetica", 12), padding=6, background="#00796b", foreground="#000000")
        self.style.map("OKButton.TButton",
            background=[('active', '#006eb3')],
            foreground=[('active', '#ffffff')])

        # Estilo para o botão "Enviar"
        self.style.configure("SendButton.TButton", font=("Helvetica", 12), padding=6, background="#009688", foreground="#000000")
        self.style.map("SendButton.TButton",
            background=[('active', '#00796b')],
            foreground=[('active', '#ffffff')])

        # Estilo para o botão "Recomeçar"
        self.style.configure("RestartButton.TButton", font=("Helvetica", 12), padding=6, background="#d32f2f", foreground="#000000")
        self.style.map("RestartButton.TButton",
            background=[('active', '#b71c1c')],
            foreground=[('active', '#ffffff')])

        # Estilo para o campo de entrada
        self.style.configure("TEntry", fieldbackground="#2d0052", background="#2d0052", foreground="#000000")

        self.username = None
        self.setup_initial_screen()

    def setup_initial_screen(self):
        self.initial_frame = ttk.Frame(self.master, style="TFrame")
        self.initial_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        ttk.Label(self.initial_frame, text="Digite seu nome:", font=("Helvetica", 16), background="#2d0052", foreground="#ffffff").pack(pady=10)

        self.name_entry = ttk.Entry(self.initial_frame, style="TEntry", font=("Helvetica", 12))
        self.name_entry.pack(pady=5)

        ttk.Button(self.initial_frame, text="OK", command=self.start_game, style="OKButton.TButton").pack(pady=10)

    def start_game(self):
        self.username = self.name_entry.get()
        if self.username:
            self.initial_frame.pack_forget()  # Remove a tela de entrada
            self.setup_game()

    def setup_game(self):
        self.frame = ttk.Frame(self.master, style="TFrame")
        self.frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.frame, bg="#2d0052", bd=0, highlightthickness=0)
        self.canvas.pack(pady=10, fill=tk.BOTH, expand=True)

        # Adicionar imagem de fundo
        self.add_background_image()

        # Atualizar o texto quando o canvas for redimensionado
        self.canvas.bind("<Configure>", self.update_welcome_graphic)

        self.instructions = ttk.Label(self.frame, text="Digite sua tentativa:", font=("Helvetica", 14), background="#2d0052", foreground="#ffffff")
        self.instructions.pack(pady=10)

        self.guess_entry = ttk.Entry(self.frame, style="TEntry", font=("Helvetica", 12))
        self.guess_entry.pack(pady=5)
        self.guess_entry.bind('<Return>', self.send_guess)

        ttk.Button(self.frame, text="Enviar", command=self.send_guess, style="SendButton.TButton").pack(pady=10)
        ttk.Button(self.frame, text="Recomeçar", command=self.restart_game, style="RestartButton.TButton").pack(pady=10)

        self.response_label = ttk.Label(self.frame, text="", font=("Helvetica", 14, "bold"), background="#2d0052", foreground="#ffffff")
        self.response_label.pack(pady=10)

        self.status_label = ttk.Label(self.frame, text="Conectando ao servidor...", font=("Helvetica", 10, "italic"), background="#2d0052", foreground="#ffffff")
        self.status_label.pack(pady=5)

        self.score_label = ttk.Label(self.frame, text="Placar: 0", font=("Helvetica", 14, "bold"), background="#2d0052", foreground="#ffffff")
        self.score_label.pack(pady=10)

        self.score = 0

        self.setup_connection()

    def add_background_image(self):
        try:
            # Carregar e redimensionar a imagem para se ajustar ao canvas
            image_path = "C:\\Users\\Administrator\\Desktop\\Jogo de Adivinhar\\background_image.png"
            image = Image.open(image_path)
            image = image.resize((self.canvas.winfo_width(), self.canvas.winfo_height()), Image.Resampling.LANCZOS)
            self.bg_image = ImageTk.PhotoImage(image)
            self.canvas.create_image(0, 0, anchor="nw", image=self.bg_image)
        except FileNotFoundError:
            print(f"Erro: Arquivo não encontrado no caminho {image_path}. Verifique se a imagem está no local correto.")
        except Exception as e:
            print(f"Erro ao carregar a imagem de fundo: {e}")

    def setup_connection(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client.connect(('localhost', 9999))
            if self.username:
                self.send_message(f"nome:{self.username}")
            welcome_message = self.receive_message()
            self.response_label.config(text=welcome_message)
            self.status_label.config(text="Conectado ao servidor.")
            self.update_welcome_graphic()  # Atualiza a tela de boas-vindas
            self.start_receiving()
        except Exception as e:
            messagebox.showerror("Erro de Conexão", f"Não foi possível conectar ao servidor: {e}")
            self.status_label.config(text="Erro ao conectar ao servidor.")

    def send_guess(self, event=None):
        guess = self.guess_entry.get()
        if guess:
            self.send_message(guess)
            self.guess_entry.delete(0, tk.END)

    def restart_game(self):
        try:
            self.send_message("recomecar")
        except:
            self.setup_connection()

    def send_message(self, message):
        try:
            self.client.sendall(message.encode('utf-8'))
        except (BrokenPipeError, OSError):
            self.setup_connection()
            self.client.sendall(message.encode('utf-8'))

    def receive_message(self):
        try:
            message = self.client.recv(1024).decode('utf-8')
            return message
        except:
            return "Erro ao receber mensagem do servidor."

    def start_receiving(self):
        threading.Thread(target=self.receive_messages_thread, daemon=True).start()

    def receive_messages_thread(self):
        while True:
            message = self.receive_message()
            if message:
                self.response_label.config(text=message)
                if "Parabéns" in message:
                    self.score += 1
                    self.score_label.config(text=f"Placar: {self.score}")
                    self.draw_end_graphic("success")
                elif "excedeu" in message:
                    self.draw_end_graphic("failure")
                elif "Novo jogo" in message:
                    self.update_welcome_graphic()
                if "Parabéns" in message or "excedeu" in message:
                    break

    def update_welcome_graphic(self, event=None):
        self.add_background_image()  # Atualiza a imagem de fundo
        self.canvas.delete("all")
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        # Desenhar o texto centralizado com cor de fundo
        self.canvas.create_text(canvas_width / 2, canvas_height / 2, 
                                text="Bem-vindo ao Jogo de Adivinhação!", 
                                font=("Helvetica", 24, "bold"), fill="#ffffff", anchor="center")

    def draw_end_graphic(self, result):
        self.canvas.delete("all")

        # Definir dimensões e posição
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        oval_width = 250
        oval_height = 120
        oval_x0 = (canvas_width - oval_width) / 2
        oval_y0 = (canvas_height - oval_height) / 2
        oval_x1 = oval_x0 + oval_width
        oval_y1 = oval_y0 + oval_height
        text_x = canvas_width / 2
        text_y = canvas_height / 2

        # Desenhar a forma (oval) com cores agradáveis
        if result == "success":
            self.canvas.create_oval(oval_x0, oval_y0, oval_x1, oval_y1, fill="#1b5e20", outline="")
            message = "Parabéns!\nVocê acertou!"
        else:
            self.canvas.create_oval(oval_x0, oval_y0, oval_x1, oval_y1, fill="#b71c1c", outline="")
            message = "Fim de Jogo!\nVocê perdeu."

        # Desenhar o texto com cor contrastante
        self.canvas.create_text(text_x, text_y, text=message, font=("Helvetica", 18, "bold"), fill="#ffffff", anchor="center")

def main():
    root = tk.Tk()
    app = GuessingGameClient(root)
    root.mainloop()

if __name__ == "__main__":
    main()
