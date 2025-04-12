import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from tkcalendar import DateEntry
import sqlite3
from openpyxl import Workbook
import os
from tkinter import messagebox

def exportar_para_excel():
    try:
        db_path = "rastreamento.db"
        pasta_saida = "exportados"
        os.makedirs(pasta_saida, exist_ok=True)

        def exportar_tabela(nome_tabela):
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            cursor.execute(f"SELECT * FROM {nome_tabela}")
            dados = cursor.fetchall()
            colunas = [descricao[0] for descricao in cursor.description]

            wb = Workbook()
            ws = wb.active
            ws.title = nome_tabela
            ws.append(colunas)
            for linha in dados:
                ws.append(linha)

            caminho_arquivo = os.path.join(pasta_saida, f"{nome_tabela}.xlsx")
            wb.save(caminho_arquivo)
            conn.close()

        exportar_tabela("registros")
        exportar_tabela("reprovacoes")

        messagebox.showinfo("Exportação concluída", "Dados exportados para a pasta 'exportados' com sucesso!")

    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao exportar: {e}")


def aba_bipador(frame, operador):
    tk.Label(frame, text="Escaneie o QR Code:", font=("Arial", 12, "bold")).pack(pady=10)
    entrada = tk.Entry(frame, width=40, font=("Arial", 11))
    entrada.pack(pady=5)

    fase_var = tk.StringVar()
    tk.Label(frame, text="Fase:", font=("Arial", 12)).pack()
    frame_fase = tk.Frame(frame)
    frame_fase.pack(pady=5)
    tk.Radiobutton(frame_fase, text="BOT", variable=fase_var, value="BOT", font=("Arial", 10)).pack(side=tk.LEFT, padx=10)
    tk.Radiobutton(frame_fase, text="TOP", variable=fase_var, value="TOP", font=("Arial", 10)).pack(side=tk.LEFT, padx=10)

    status_label = tk.Label(frame, text="", font=("Arial", 10))
    status_label.pack(pady=5)
        # Variável de controle do último QR lido
    ultimo_qr_lido = {"valor": ""}

    def verificar_entrada(event=None):
        qr_data = entrada.get().strip()

        # Confere se tem 5 partes separadas por "-"
        partes = qr_data.split("-")
        if len(partes) == 5 and all(partes):
            # Confere se última parte tem 2 ou 3 caracteres
            if len(partes[4]) in [2, 3]:
                # Se for diferente do último lido, registra
                if qr_data != ultimo_qr_lido["valor"]:
                    ultimo_qr_lido["valor"] = qr_data
                    salvar()

    entrada.bind("<KeyRelease>", verificar_entrada)


    def salvar(event=None):
        qr_data = entrada.get().strip()
        fase = fase_var.get()
        if not qr_data or not fase:
            status_label.config(text="QR Code ou Fase não informados!", fg="red")
            return

        partes = qr_data.split("-")
        if len(partes) < 5:
            status_label.config(text="Formato do QR Code inválido!", fg="red")
            return

        numero_serie = partes[0]
        ordem_producao = partes[1]
        modelo_placa = partes[2]
        linha_producao = f"{partes[3].strip().upper()}-{partes[4].strip()}"
        linha_producao = linha_producao.strip().upper()
        turno = obter_turno()

        linhas_validas_formatadas = [linha.strip().upper() for linha in LINHAS_VALIDAS]
        if linha_producao not in linhas_validas_formatadas:
            linha_producao = "Desconhecida"

        conn = sqlite3.connect("rastreamento.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM registros WHERE numero_serie=? AND ordem_producao=? AND fase=?",
                       (numero_serie, ordem_producao, fase))
        if cursor.fetchone()[0] > 0:
            status_label.config(text=f"Placa {numero_serie} já registrada!", fg="red")
        else:
            cursor.execute("""
                INSERT INTO registros (data_hora, operador, numero_serie, ordem_producao, modelo_placa, linha_producao, turno, fase, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), operador, numero_serie, ordem_producao, modelo_placa, linha_producao, turno, fase, "Aprovada"))
            conn.commit()
            status_label.config(text=f"Placa {numero_serie} registrada com sucesso!", fg="green")
        conn.close()
        entrada.delete(0, tk.END)
        entrada.focus_set()


    entrada.bind("<Return>", salvar)
    tk.Button(frame, text="Salvar", command=salvar, font=("Arial", 10, "bold"), bg="#4CAF50", fg="white").pack(pady=10)

def mostrar_placas_registradas(frame):
    tk.Label(frame, text="Histórico de Placas Registradas", font=("Arial", 16, "bold")).pack(pady=10)

    colunas = ("Número de Série", "Ordem de Produção", "Modelo", "Linha", "Turno",
               "Data e Hora", "Operador", "Status")
    tree = ttk.Treeview(frame, columns=colunas, show='headings')

    for col in colunas:
        tree.heading(col, text=col)
        tree.column(col, width=120, anchor="center")  # Centraliza o conteúdo

    tree.pack(fill='both', expand=True, pady=10)

    contador_label = tk.Label(frame, text="", font=("Arial", 9), fg="gray")
    contador_label.pack(pady=(0, 5))

    def carregar():
        for i in tree.get_children():
            tree.delete(i)

        conn = sqlite3.connect('rastreamento.db')
        cursor = conn.cursor()

        cursor.execute("""
            SELECT numero_serie, ordem_producao, modelo_placa, linha_producao, turno, data_hora, operador, status 
            FROM registros
        """)
        registros = cursor.fetchall()

        for registro in registros:
            tree.insert('', 'end', values=registro)

        cursor.execute("""
            SELECT ordem_producao, COUNT(*) FROM registros 
            GROUP BY ordem_producao
        """)
        contagens = cursor.fetchall()
        texto = "Qtd por OP: " + ", ".join([f"{op} ({qtd})" for op, qtd in contagens])
        contador_label.config(text=texto)

        conn.close()
    tk.Button(frame, text="Exportar para Excel", command=exportar_para_excel, font=("Arial", 10, "bold"), bg="#4CAF50", fg="white").pack(pady=10)

    tk.Button(frame, text="Atualizar", command=carregar, font=("Arial", 10, "bold"), bg="#2196F3", fg="white").pack(pady=5)
    carregar()


def aba_reprovadas(frame, operador):
    tk.Label(frame, text="Escaneie o QR Code:", font=("Arial", 12, "bold")).pack(pady=10)
    entrada = tk.Entry(frame, width=40, font=("Arial", 11))
    entrada.pack(pady=5)

    tk.Label(frame, text="Motivo da Reprovação:", font=("Arial", 12)).pack(pady=10)
    motivo_var = tk.StringVar()
    motivos = ["Curto-circuito", "Falha no componente", "Erro de soldagem", "Dano físico", "Outros"]
    menu = ttk.Combobox(frame, textvariable=motivo_var, values=motivos, state="readonly", font=("Arial", 10))
    menu.pack(pady=5)

    def salvar():
        qr_data = entrada.get()
        motivo = motivo_var.get()
        if not qr_data or not motivo:
            messagebox.showerror("Erro", "QR Code ou motivo não informado!")
            return
        try:
            partes = qr_data.split("-")
            numero_serie, ordem_producao, modelo_placa = partes[:3]
            linha_producao = partes[3] if len(partes) > 3 else "Desconhecida"
            turno = obter_turno()
            status = "Reprovada para Retrabalho"
            conn = sqlite3.connect("rastreamento.db")
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO reprovacoes (numero_serie, ordem_producao, modelo_placa, linha_producao, operador, turno, data_hora, motivo, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (numero_serie, ordem_producao, modelo_placa, linha_producao, operador, turno, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), motivo, status))
            conn.commit()
            messagebox.showinfo("Sucesso", f"Placa {numero_serie} registrada como reprovada!")
            conn.close()
            entrada.delete(0, tk.END)
            motivo_var.set("")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    tk.Button(frame, text="Registrar Reprovada", command=salvar, font=("Arial", 10, "bold"), bg="#F44336", fg="white").pack(pady=10)

def aba_historico(frame):
    colunas = ("Nº de Série", "Ordem de Produção", "Modelo", "Linha", "Operador", "Turno", "Data e Hora", "Motivo", "Status")
    tree = ttk.Treeview(frame, columns=colunas, show="headings", height=15)

    for coluna in colunas:
        tree.heading(coluna, text=coluna)
        tree.column(coluna, width=120, anchor="center")

    tree.pack(expand=True, fill="both", padx=10, pady=10)

    def carregar():
        for row in tree.get_children():
            tree.delete(row)
        conn = sqlite3.connect("rastreamento.db")
        cursor = conn.cursor()
        cursor.execute("SELECT numero_serie, ordem_producao, modelo_placa, linha_producao, operador, turno, data_hora, motivo, status FROM reprovacoes")
        for row in cursor.fetchall():
            tree.insert("", "end", values=row)
        conn.close()
    tk.Button(frame, text="Exportar para Excel", command=exportar_para_excel, font=("Arial", 10, "bold"), bg="#4CAF50", fg="white").pack(pady=10)

    tk.Button(frame, text="Atualizar", command=carregar, font=("Arial", 10, "bold")).pack(pady=10)
    carregar()

def obter_turno():
    hora = datetime.now().time()
    if datetime.strptime("06:00", "%H:%M").time() <= hora < datetime.strptime("14:20", "%H:%M").time():
        return "1º Turno"
    elif datetime.strptime("14:20", "%H:%M").time() <= hora < datetime.strptime("22:35", "%H:%M").time():
        return "2º Turno"
    else:
        return "3º Turno"

LINHAS_VALIDAS = ["SMT1-01", "SMT3-004", "SMT3-01", "SMT3-02", "SMT3-03", "SMT3-05"]

def iniciar_interface(nome_operador):
    root = tk.Tk()
    root.title(f"Sistema de Rastreabilidade - Operador: {nome_operador}")
    root.geometry("950x650")

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)

    frame_bipador = tk.Frame(notebook)
    frame_registradas = tk.Frame(notebook)
    frame_reprovadas = tk.Frame(notebook)
    frame_historico = tk.Frame(notebook)

    notebook.add(frame_bipador, text="Bipador")
    notebook.add(frame_registradas, text="Placas Registradas")
    notebook.add(frame_reprovadas, text="Registrar Reprovadas")
    notebook.add(frame_historico, text="Histórico de Reprovações")

    aba_bipador(frame_bipador, nome_operador)
    mostrar_placas_registradas(frame_registradas)
    aba_reprovadas(frame_reprovadas, nome_operador)
    aba_historico(frame_historico)

    root.mainloop()
