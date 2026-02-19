import tkinter as tk
import logging
from datetime import datetime
from tkinter import messagebox, ttk

try:
    import customtkinter as ctk
except ImportError:
    ctk = None

from .constants import (
    CANCEL_REQUIRED,
    CREATE_REQUIRED,
    EDITABLE_FIELDS,
    FIELD_LABELS,
    FINALIZE_REQUIRED,
    STATUS_CANCELADO,
    STATUS_FINALIZADO,
    STATUS_MONITORADO,
    STATUS_OPCOES,
)
from .validators import normalize_and_validate

logger = logging.getLogger(__name__)


def format_talao(ano, numero):
    try:
        return f"{int(numero):04d}/{int(ano)}"
    except (TypeError, ValueError):
        return f"{numero or '----'}/{ano or '----'}"


class TalaoEditor(tk.Toplevel):
    def __init__(self, parent, repo, talao_id, intervalo_min, on_saved):
        super().__init__(parent)
        self.repo = repo
        self.talao_id = talao_id
        self.on_saved = on_saved
        self.title("Editar Talão")
        self.geometry("650x620")
        self.resizable(False, False)

        self.widgets = {}
        self.intervalo_var = tk.StringVar(value=str(intervalo_min))

        row = 0
        record = self.repo.get_talao(talao_id)
        if not record:
            messagebox.showerror("Erro", "Talão não encontrado.")
            self.destroy()
            return
        self.record = record

        tk.Label(self, text=f"Talão {format_talao(record.get('ano'), record.get('talao'))}", font=("Arial", 12, "bold")).grid(
            row=row, column=0, columnspan=2, sticky="w", padx=12, pady=(10, 12)
        )
        row += 1

        for key in EDITABLE_FIELDS:
            tk.Label(self, text=FIELD_LABELS[key]).grid(row=row, column=0, sticky="w", padx=12, pady=4)

            if key == "status":
                widget = ttk.Combobox(self, values=STATUS_OPCOES, state="readonly")
                widget.set(str(record.get(key) or STATUS_MONITORADO))
            elif key == "observacao":
                widget = tk.Text(self, height=4, width=40)
                widget.insert("1.0", str(record.get(key) or ""))
            else:
                widget = tk.Entry(self, width=45)
                value = record.get(key)
                if value is None:
                    value_str = ""
                elif key == "data_bo":
                    value_str = value.strftime("%d/%m/%Y")
                else:
                    value_str = str(value)
                widget.insert(0, value_str)

            widget.grid(row=row, column=1, sticky="ew", padx=12, pady=4)
            self.widgets[key] = widget
            row += 1

        tk.Label(self, text="Intervalo de alerta (min)").grid(row=row, column=0, sticky="w", padx=12, pady=8)
        ttk.Combobox(self, textvariable=self.intervalo_var, state="readonly", values=["1", "5", "15", "30", "60"]).grid(
            row=row, column=1, sticky="w", padx=12, pady=8
        )
        row += 1

        btn = tk.Button(self, text="Salvar", bg="#1565C0", fg="white", command=self.save)
        btn.grid(row=row, column=0, columnspan=2, sticky="ew", padx=12, pady=12)

        self.columnconfigure(1, weight=1)
        self.transient(parent)
        self.grab_set()

    def _collect(self):
        data = {}
        for key in EDITABLE_FIELDS:
            widget = self.widgets[key]
            if isinstance(widget, tk.Text):
                data[key] = widget.get("1.0", tk.END).strip()
            else:
                data[key] = widget.get().strip()
        data_solic = self.record.get("data_solic")
        hora_solic = self.record.get("hora_solic")
        data["data_solic"] = data_solic.strftime("%d/%m/%Y") if data_solic else ""
        data["hora_solic"] = str(hora_solic)[:5] if hora_solic else ""
        return data

    def save(self):
        data = self._collect()
        status = data["status"]

        if status == STATUS_FINALIZADO:
            required = FINALIZE_REQUIRED
        elif status == STATUS_CANCELADO:
            required = CANCEL_REQUIRED
        else:
            required = CREATE_REQUIRED

        try:
            normalized, missing = normalize_and_validate(data, required)
        except ValueError as exc:
            messagebox.showwarning("Validacao", str(exc))
            return

        if missing:
            messagebox.showwarning("Validação", "Campos obrigatórios:\n- " + "\n- ".join(missing))
            return

        try:
            self.repo.update_talao(self.talao_id, normalized, int(self.intervalo_var.get()))
            self.on_saved()
            self.destroy()
        except Exception:
            logger.exception("Falha ao atualizar talão %s", self.talao_id)
            messagebox.showerror("Erro", "Falha ao atualizar talão. Verifique os dados e tente novamente.")


class AFISDashboard:
    ALERT_POLL_MS = 60000

    def __init__(self, root, repo):
        self.root = root
        self.repo = repo

        self.root.title("Registro AFIS - CECOP")
        self.root.geometry("1080x760")

        self.intervalo_map = {
            "1 min": 1,
            "5 min": 5,
            "15 min": 15,
            "30 min (padrao)": 30,
            "60 min": 60,
        }

        self.widgets = {}
        self.proximo_talao_var = tk.StringVar(value="-")
        self.alerta_var = tk.StringVar(value="30 min (padrão)")

        self._build_layout()
        self._set_defaults()
        self.refresh_tree()
        self.root.after(self.ALERT_POLL_MS, self.processar_alertas)

    def _build_layout(self):
        titulo = tk.Label(self.root, text="Registro Digital de Talões AFIS", font=("Arial", 16, "bold"))
        titulo.pack(pady=10)

        form = tk.LabelFrame(self.root, text="Cadastro de Talão", padx=10, pady=10)
        form.pack(fill="x", padx=12, pady=6)

        info = tk.Frame(form)
        info.grid(row=0, column=0, columnspan=4, sticky="ew", pady=(0, 6))
        tk.Label(info, text="Próximo Talão (ano atual):", font=("Arial", 9, "bold")).pack(side="left")
        tk.Label(info, textvariable=self.proximo_talao_var, fg="#0D47A1", font=("Arial", 9, "bold")).pack(side="left", padx=6)

        layout_fields = [
            "delegacia",
            "autoridade",
            "solicitante",
            "endereco",
            "boletim",
            "natureza",
            "data_bo",
            "vitimas",
            "equipe",
            "operador",
            "status",
            "observacao",
        ]

        row = 1
        col = 0
        for key in layout_fields:
            tk.Label(form, text=FIELD_LABELS[key]).grid(row=row, column=col, sticky="w", pady=4, padx=4)

            if key == "status":
                widget = ttk.Combobox(form, values=STATUS_OPCOES, state="readonly", width=28)
                widget.set(STATUS_MONITORADO)
            elif key == "observacao":
                widget = tk.Text(form, width=35, height=3)
            else:
                widget = tk.Entry(form, width=32)

            widget.grid(row=row, column=col + 1, sticky="ew", pady=4, padx=4)
            self.widgets[key] = widget

            if col == 2:
                col = 0
                row += 1
            else:
                col = 2

        row += 1
        tk.Label(form, text="Intervalo de alerta").grid(row=row, column=0, sticky="w", padx=4, pady=8)
        combo_alerta = ttk.Combobox(form, textvariable=self.alerta_var, state="readonly", values=list(self.intervalo_map.keys()))
        combo_alerta.grid(row=row, column=1, sticky="w", padx=4, pady=8)

        botoes = tk.Frame(form)
        botoes.grid(row=row, column=2, columnspan=2, sticky="ew", padx=4, pady=8)
        tk.Button(botoes, text="Salvar", bg="#2E7D32", fg="white", command=self.criar_talao).pack(side="left", padx=4)
        tk.Button(botoes, text="Editar", bg="#1565C0", fg="white", command=self.editar_selecionado).pack(side="left", padx=4)
        tk.Button(botoes, text="Atualizar", command=self.refresh_tree).pack(side="left", padx=4)
        tk.Button(botoes, text="Limpar", command=self._set_defaults).pack(side="left", padx=4)

        for col_idx in (1, 3):
            form.grid_columnconfigure(col_idx, weight=1)

        list_frame = tk.LabelFrame(self.root, text="Talões visíveis", padx=10, pady=10)
        list_frame.pack(fill="both", expand=True, padx=12, pady=8)

        cols = ("talao", "boletim", "delegacia", "natureza", "status")
        self.tree = ttk.Treeview(list_frame, columns=cols, show="headings", height=15)
        self.tree.heading("talao", text="Talão")
        self.tree.heading("boletim", text="Boletim")
        self.tree.heading("delegacia", text="Delegacia")
        self.tree.heading("natureza", text="Natureza")
        self.tree.heading("status", text="Status")

        self.tree.column("talao", width=90, anchor="center")
        self.tree.column("boletim", width=120, anchor="center")
        self.tree.column("delegacia", width=220)
        self.tree.column("natureza", width=240)
        self.tree.column("status", width=120, anchor="center")

        self.tree.tag_configure(STATUS_MONITORADO, background="#FFFDE7")
        self.tree.tag_configure(STATUS_FINALIZADO, background="#E8F5E9")
        self.tree.tag_configure(STATUS_CANCELADO, background="#FFEBEE")

        self.tree.pack(fill="both", expand=True)

    def _set_defaults(self):
        defaults = {
            "status": STATUS_MONITORADO,
            "data_bo": "",
            "delegacia": "",
            "autoridade": "",
            "solicitante": "",
            "endereco": "",
            "boletim": "",
            "natureza": "",
            "vitimas": "",
            "equipe": "",
            "operador": "",
            "observacao": "",
        }

        for key, widget in self.widgets.items():
            value = defaults.get(key, "")
            if isinstance(widget, tk.Text):
                widget.delete("1.0", tk.END)
                widget.insert("1.0", value)
            elif isinstance(widget, ttk.Combobox):
                widget.set(value)
            else:
                widget.delete(0, tk.END)
                widget.insert(0, value)

        self._refresh_proximo_talao()

    def _collect_form_data(self):
        data = {}
        for key, widget in self.widgets.items():
            if isinstance(widget, tk.Text):
                data[key] = widget.get("1.0", tk.END).strip()
            else:
                data[key] = widget.get().strip()
        return data

    def _refresh_proximo_talao(self):
        try:
            ano = datetime.now().year
            numero = self.repo.get_next_talao(ano)
            self.proximo_talao_var.set(format_talao(ano, numero))
        except Exception:
            self.proximo_talao_var.set("indisponível")

    def criar_talao(self):
        data = self._collect_form_data()
        now = datetime.now()
        data["data_solic"] = now.strftime("%d/%m/%Y")
        data["hora_solic"] = now.strftime("%H:%M")
        data["status"] = STATUS_MONITORADO

        try:
            normalized, missing = normalize_and_validate(data, CREATE_REQUIRED)
        except ValueError as exc:
            messagebox.showwarning("Validação", str(exc))
            return

        if missing:
            messagebox.showwarning("Validação", "Campos obrigatórios:\n- " + "\n- ".join(missing))
            return

        intervalo = self.intervalo_map[self.alerta_var.get()]

        try:
            novo_talao = self.repo.insert_talao(normalized, intervalo)
            messagebox.showinfo("Sucesso", f"Talão {format_talao(now.year, novo_talao)} registrado com status monitorado.")
            self._set_defaults()
            self.refresh_tree()
        except Exception:
            logger.exception("Falha ao gravar novo talão")
            messagebox.showerror("Erro", "Falha ao gravar talão. Verifique os dados e tente novamente.")

    def editar_selecionado(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Selecione um talão na lista.")
            return

        item_id = selected[0]
        valores = self.tree.item(item_id).get("values", [])
        status_atual = str(valores[4]).strip().lower() if len(valores) >= 5 else ""
        if status_atual in (STATUS_FINALIZADO, STATUS_CANCELADO):
            messagebox.showinfo("Info", "Talões finalizados ou cancelados não podem ser editados.")
            return

        talao_id = int(item_id)
        intervalo = self.intervalo_map[self.alerta_var.get()]
        TalaoEditor(self.root, self.repo, talao_id, intervalo, self.refresh_tree)

    def refresh_tree(self):
        for iid in self.tree.get_children():
            self.tree.delete(iid)

        try:
            rows = self.repo.list_initial_taloes()
        except Exception:
            logger.exception("Falha ao carregar talões")
            messagebox.showerror("Erro", "Falha ao carregar talões.")
            return

        for row in rows:
            talao_id, ano, talao, boletim, delegacia, natureza, status = row
            self.tree.insert(
                "",
                "end",
                iid=str(talao_id),
                values=(format_talao(ano, talao), boletim or "", delegacia or "", natureza or "", status),
                tags=(status,),
            )

        self._refresh_proximo_talao()

    def processar_alertas(self):
        try:
            due_rows = self.repo.list_due_monitoring()
        except Exception:
            self.root.after(self.ALERT_POLL_MS, self.processar_alertas)
            return

        # Processa apenas um alerta por ciclo para evitar sequência de pop-ups
        # e garantir foco no preenchimento/validação do talão em questão.
        for row in due_rows:
            talao_id, intervalo_min, ano, talao, boletim, status = row
            if status != STATUS_MONITORADO:
                continue

            self.root.bell()
            pergunta = (
                f"Talão {format_talao(ano, talao)} (Boletim: {boletim or 'sem boletim'}) segue monitorado.\n\n"
                "As ações necessárias para encerrar o monitoramento já foram cumpridas?"
            )
            confirmar = messagebox.askyesno("Alerta de monitoramento", pergunta)

            if confirmar:
                self._tentar_finalizar_por_alerta(talao_id, intervalo_min)
            else:
                self.repo.postpone_monitoring(talao_id, intervalo_min)
            break

        self.root.after(self.ALERT_POLL_MS, self.processar_alertas)

    def _tentar_finalizar_por_alerta(self, talao_id, intervalo_min):
        record = self.repo.get_talao(talao_id)
        if not record:
            return

        data = {key: "" for key in EDITABLE_FIELDS}
        for key in EDITABLE_FIELDS:
            value = record.get(key)
            if value is None:
                data[key] = ""
            elif key == "data_bo":
                data[key] = value.strftime("%d/%m/%Y")
            else:
                data[key] = str(value)
        data_solic = record.get("data_solic")
        hora_solic = record.get("hora_solic")
        data["data_solic"] = data_solic.strftime("%d/%m/%Y") if data_solic else ""
        data["hora_solic"] = str(hora_solic)[:5] if hora_solic else ""

        data["status"] = STATUS_FINALIZADO

        try:
            normalized, missing = normalize_and_validate(data, FINALIZE_REQUIRED)
        except ValueError as exc:
            messagebox.showwarning("Validação", str(exc))
            self.repo.postpone_monitoring(talao_id, intervalo_min)
            TalaoEditor(self.root, self.repo, talao_id, intervalo_min, self.refresh_tree)
            return

        if missing:
            messagebox.showwarning(
                "Pendências",
                "Não foi possível finalizar automaticamente. Campos obrigatórios ausentes:\n- "
                + "\n- ".join(missing),
            )
            self.repo.postpone_monitoring(talao_id, intervalo_min)
            TalaoEditor(self.root, self.repo, talao_id, intervalo_min, self.refresh_tree)
            return

        try:
            self.repo.update_talao(talao_id, normalized, intervalo_min)
            self.refresh_tree()
        except Exception:
            logger.exception("Falha ao finalizar talão %s", talao_id)
            messagebox.showerror("Erro", "Falha ao finalizar talão.")


def build_root():
    if ctk is not None:
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        return ctk.CTk()
    return tk.Tk()
