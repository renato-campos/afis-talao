import logging
from afis_app.config import load_env_file
from tkinter import messagebox

from afis_app.repository import SQLServerRepository
from afis_app.ui import AFISDashboard, build_root


def main():
    load_env_file()
    logging.basicConfig(
        filename="afis_app.log",
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )
    root = build_root()

    try:
        repository = SQLServerRepository()
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
