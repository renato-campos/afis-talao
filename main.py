import logging
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

from afis_app.config import get_env, load_env_file
from afis_app.interfaces import TalaoRepository
from afis_app.repository import SQLServerRepository
from afis_app.ui import AFISDashboard, build_root


def _resolve_asset_path(path_value):
    if not path_value:
        return None
    candidate = Path(path_value).expanduser()
    if candidate.is_absolute():
        return candidate
    project_root = Path(__file__).resolve().parent
    return (project_root / candidate).resolve()


def _configure_app_icon(root):
    icon_path = _resolve_asset_path(get_env("APP_ICON_PATH"))
    if not icon_path or not icon_path.exists():
        return
    try:
        suffix = icon_path.suffix.lower()
        if suffix == ".ico":
            # Windows .ico é suportado por iconbitmap; PhotoImage não abre .ico.
            root.iconbitmap(default=str(icon_path))
            return

        img = tk.PhotoImage(file=str(icon_path))
        root.iconphoto(True, img)
        root._app_icon_ref = img
    except Exception:
        logging.getLogger(__name__).warning("Falha ao carregar ícone do app em %s", icon_path, exc_info=True)


def main():
    load_env_file()
    logging.basicConfig(
        filename="afis_app.log",
        encoding="utf-8",
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )
    root = build_root()
    _configure_app_icon(root)

    try:
        repository: TalaoRepository = SQLServerRepository()
    except Exception:
        logging.getLogger(__name__).exception("Falha na inicialização da aplicação")
        messagebox.showerror(
            "Erro de inicialização",
            "Não foi possível inicializar o aplicativo ou conectar ao SQL Server.",
        )
        root.destroy()
        raise SystemExit(1)

    AFISDashboard(root, repository)
    root.mainloop()


if __name__ == "__main__":
    main()
