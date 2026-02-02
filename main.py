import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkinter import simpledialog
import threading
import time
import os
import tempfile
from datetime import datetime


class TalaoMonitor:
    """Classe para gerenciar cada Talão individualmente"""

    def __init__(self, app, item_id, dados, tempo_segundos):
        self.app = app
        self.item_id = item_id  # ID na tabela visual
        self.dados = dados
        self.stop_event = threading.Event()
        self.tempo_segundos = tempo_segundos

        # Inicia o monitoramento em background
        self.thread = threading.Thread(target=self.loop_monitoramento, daemon=True)
        self.thread.start()

    def loop_monitoramento(self):
        # Loop principal do BO
        while not self.stop_event.is_set():
            # Conta o tempo fracionado (para poder parar rápido)
            for _ in range(self.tempo_segundos):
                if self.stop_event.is_set():
                    return
                time.sleep(1)

            # Se chegou aqui, o tempo acabou e não foi parado. Mostra Alerta.
            if not self.stop_event.is_set():
                self.mostrar_alerta()

    def mostrar_alerta(self):
        # Toca som
        self.app.root.bell()

        talao = self.dados.get("TALÃO", "---")
        rdo = self.dados.get("RDO", "---")

        msg = (
            f"ALERTA DE PENDÊNCIA!\n\n"
            f"1) O RDO: {rdo} (Talão {talao}) já finalizou?\n"
            f"2) Já enviou no grupo AFIS?\n\n"
            "Clique em SIM para finalizar este monitoramento.\n"
            "Clique em NÃO para ser lembrado novamente."
        )

        # Usamos invoke para garantir thread-safety com Tkinter
        resposta = messagebox.askyesno(f"Alerta: Talão {talao}", msg)

        if resposta:
            self.finalizar()
        else:
            # Não faz nada, o loop while continua e vai contar o tempo de novo
            pass

    def finalizar(self):
        self.stop_event.set()

        # Pega a hora exata do término
        hora_fim = datetime.now().strftime("%H:%M")

        # Atualiza a cor na tabela para Verde
        self.app.tree.item(self.item_id, tags=('finalizado',))

        # Atualiza o Status e a Hora de Término
        self.app.tree.set(self.item_id, "Status", "FINALIZADO")
        self.app.tree.set(self.item_id, "Hora Término", hora_fim)


class AFISDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Bot AFIS - Painel de Controle")
        self.root.geometry("950x600")

        # Dicionário para guardar os monitores ativos: {item_id: ObjetoBOMonitor}
        self.monitores_ativos = {}

        # --- Cabeçalho ---
        lbl_title = tk.Label(root, text="Painel de Controle AFIS", font=("Arial", 16, "bold"))
        lbl_title.pack(pady=10)

        # Botão de Instruções
        btn_help = tk.Button(root, text="( ? ) MANUAL E INSTRUÇÕES DE USO", bg="#0288D1", fg="white",
                             font=("Arial", 9, "bold"), command=self.show_instructions)
        btn_help.pack(pady=2)

        # --- Área de Cadastro ---
        frame_form = tk.LabelFrame(root, text="Novo Registro", padx=10, pady=10)
        frame_form.pack(padx=15, pady=5, fill="x")

        self.fields = ["TALÃO", "DISTRITO", "AUTORIDADE", "NATUREZA", "ENDEREÇO", "RDO"]
        self.entries = {}

        # Grid para economizar espaço
        for i, field in enumerate(self.fields):
            lbl = tk.Label(frame_form, text=field, font=("Arial", 9, "bold"))
            lbl.grid(row=i, column=0, sticky="w", pady=2)

            ent = tk.Entry(frame_form)
            ent.grid(row=i, column=1, sticky="ew", padx=5, pady=2)
            frame_form.grid_columnconfigure(1, weight=1)  # Estica o campo
            self.entries[field] = ent

        # --- Seletor de Tempo ---
        frame_time = tk.Frame(frame_form)
        frame_time.grid(row=len(self.fields), column=0, columnspan=2, pady=10, sticky="ew")

        tk.Label(frame_time, text="Tempo de Alerta:").pack(side="left")

        # Definição das opções
        self.time_options = {
            "5 Segundos (Modo Teste)": 5,
            "15 Minutos": 900,
            "30 Minutos (Padrão)": 1800,
            "1 Hora": 3600
        }
        self.timer_var = tk.StringVar()
        self.combo_timer = ttk.Combobox(frame_time, textvariable=self.timer_var, state="readonly", width=25)
        self.combo_timer['values'] = list(self.time_options.keys())

        # --- DEFINIÇÃO DO PADRÃO ---
        # Força o valor exato para evitar erros de índice
        self.combo_timer.set("30 Minutos (Padrão)")

        self.combo_timer.pack(side="left", padx=5)

        # Botão Adicionar
        btn_add = tk.Button(frame_form, text="+ ADICIONAR À LISTA E MONITORAR", bg="#4CAF50", fg="white",
                            font=("Arial", 10, "bold"), command=self.adicionar_monitoramento)
        btn_add.grid(row=len(self.fields) + 1, column=0, columnspan=2, sticky="ew", pady=10)

        # --- LISTA DE MONITORAMENTO (Treeview) ---
        lbl_list = tk.Label(root, text="Monitoramento em Tempo Real", font=("Arial", 12, "bold"))
        lbl_list.pack(pady=(15, 5))

        # Colunas
        cols = ("Data", "Talão", "RDO", "Hora Início", "Hora Término", "Tempo", "Status", "Operador")
        self.tree = ttk.Treeview(root, columns=cols, show='headings', height=10)

        # Configurar colunas
        self.tree.heading("Data", text="Data")
        self.tree.column("Data", width=80, anchor="center")

        self.tree.heading("Talão", text="Talão")
        self.tree.column("Talão", width=60, anchor="center")

        self.tree.heading("RDO", text="RDO")
        self.tree.column("RDO", width=100, anchor="center")

        self.tree.heading("Hora Início", text="Início")
        self.tree.column("Hora Início", width=70, anchor="center")

        self.tree.heading("Hora Término", text="Término")
        self.tree.column("Hora Término", width=70, anchor="center")

        self.tree.heading("Tempo", text="Timer")
        self.tree.column("Tempo", width=80, anchor="center")

        self.tree.heading("Status", text="Status")
        self.tree.column("Status", width=100, anchor="center")

        self.tree.heading("Operador", text="Operador")
        self.tree.column("Operador", width=80, anchor="center")

        self.tree.pack(padx=15, fill="both", expand=True)

        # Configurar Cores das linhas
        self.tree.tag_configure('ativo', background='white')
        self.tree.tag_configure('finalizado', background='#d4edda', foreground='#155724')  # Verde claro

        # Botão para finalizar manual
        btn_stop = tk.Button(root, text="BAIXAR / FINALIZAR SELECIONADO", bg="#FF9800", fg="white",
                             command=self.baixar_manual)
        btn_stop.pack(pady=10, fill="x", padx=15)

    def adicionar_monitoramento(self):
        # 1. Coleta dados
        dados = {}
        for field, entry in self.entries.items():
            valor = entry.get().strip()
            dados[field] = valor

        # Validação básica
        if not dados["TALÃO"] and not dados["RDO"]:
            messagebox.showwarning("Atenção", "Preencha pelo menos o Talão ou o RDO.")
            return

        # Pergunta o Operador
        sigla_operador = simpledialog.askstring(
            "Entrada de Dados",
            "Qual a sigla do operador responsável pelo recebimento do AFIS?"
        )

        if sigla_operador is None:
            return

        sigla_formatada = sigla_operador.strip().upper() if sigla_operador.strip() else "---"

        # 2. Gera TXT Temporário
        self.gerar_txt(dados)

        # 3. Adiciona na Tabela Visual
        data_atual = datetime.now().strftime("%d/%m/%Y")
        hora_inicio = datetime.now().strftime("%H:%M")
        nome_tempo = self.timer_var.get()
        tempo_seg = self.time_options.get(nome_tempo, 1800)  # Padrão 30 min se algo der errado

        # Insere na treeview
        item_id = self.tree.insert("", "end", values=(
            data_atual,
            dados["TALÃO"],
            dados["RDO"],
            hora_inicio,
            "-",
            nome_tempo,
            "MONITORANDO",
            sigla_formatada
        ), tags=('ativo',))

        # 4. Cria o Robô (Monitor)
        novo_monitor = TalaoMonitor(self, item_id, dados, tempo_seg)
        self.monitores_ativos[item_id] = novo_monitor

        # 5. Limpa campos
        self.limpar_campos()

    def baixar_manual(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Selecione um item na lista para baixar.")
            return

        item_id = selected[0]

        status_atual = self.tree.item(item_id)['values'][6]
        if status_atual == "FINALIZADO":
            return

        if item_id in self.monitores_ativos:
            monitor = self.monitores_ativos[item_id]
            monitor.finalizar()
            messagebox.showinfo("Sucesso", "BO Baixado manualmente.")

    def gerar_txt(self, dados):
        conteudo = f"--- REGISTRO {datetime.now().strftime('%d/%m/%Y %H:%M')} ---\n\n"
        for k, v in dados.items():
            conteudo += f"{k}: {v}\n"
        conteudo += "-" * 40

        try:
            temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8')
            temp_file.write(conteudo)
            temp_file.close()
            os.startfile(temp_file.name)
        except Exception:
            pass

    def limpar_campos(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.entries["TALÃO"].focus()

    def show_instructions(self):
        msg = (
            "MANUAL DE USO - BOT AFIS \n"
            "---------------------------------------------------\n\n"
            "FINALIDADE DO APP:\n"
            "Este aplicativo auxilia o Agente de Telecomunicações responsável pela Intranet a NÃO esquecer de enviar o BO finalizado para o Grupo AFIS.\n\n"
            "⚠️ IMPORTANTE:\n"
            "1. Este robô NÃO identifica nada sozinho.\n"
            "2. Ele NÃO monitora o WhatsApp.\n"
            "3. TODAS as informações devem ser preenchidas manualmente pelo operador.\n\n"
            "SOBRE O TIMER (TEMPOS):\n"
            "• 5 Segundos (Modo Teste): Use apenas para testar se o alerta está funcionando.\n"
            "• 30 Minutos (Padrão): Tempo recomendado para aguardar o trâmite do BO.\n"
            "• 1 Hora: Quando sabe que vai demorar muito o término do BO.\n\n"
            "COMO RESPONDER AO ALERTA:\n"
            "Quando a janela de aviso aparecer perguntando se você enviou ao AFIS:\n"
            "✅ CLIQUE EM SIM: Apenas se o BO já finalizou e vc JÁ enviou no grupo AFIS. O monitoramento para e fica VERDE.\n"
            "❌ CLIQUE EM NÃO: Se o BO ainda não foi feito ou enviado. O robô vai reiniciar o timer e te avisar novamente no próximo ciclo."
        )
        messagebox.showinfo("Instruções e Manual", msg)


if __name__ == "__main__":
    root = tk.Tk()
    app = AFISDashboard(root)
    root.mainloop()