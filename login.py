import sqlite3
import tkinter as tk
from tkinter import messagebox
from interface.interface import iniciar_interface
from database.bancodedados import inicializar_banco

inicializar_banco()

def autenticar():
    matricula = entrada_matricula.get().strip()
    if not matricula:
        messagebox.showerror("Erro", "Informe a matrícula!")
        return

    conn = sqlite3.connect("rastreamento.db")
    cursor = conn.cursor()
    cursor.execute("SELECT nome FROM usuarios WHERE matricula=?", (matricula,))
    resultado = cursor.fetchone()
    conn.close()

    if resultado:
        nome = resultado[0]
        root.destroy()
        iniciar_interface(matricula)
    else:
        messagebox.showerror("Erro", "Matrícula não encontrada!")

root = tk.Tk()
root.title("Login")
root.geometry("300x150")

tk.Label(root, text="Matrícula do Operador:").pack(pady=10)
entrada_matricula = tk.Entry(root)
entrada_matricula.pack(pady=5)

tk.Button(root, text="Entrar", command=autenticar).pack(pady=10)

root.mainloop()
