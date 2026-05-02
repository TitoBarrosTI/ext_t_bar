# Ex_T_Bar

> Agrupador de atalhos para a barra de tarefas do Windows 11.

![Ex_T_Bar popup](screenshot.png)

O Windows 11 não oferece agrupamento nativo de ícones na taskbar. O **Ex_T_Bar** resolve isso — um único ícone fixado que, ao ser clicado, exibe um popup com seus atalhos organizados por categoria.

---

## Funcionalidades

- Popup posicionado automaticamente acima do ícone na taskbar
- Organização de atalhos em grupos (Dev, Design, Office, etc.)
- Navegação por hover entre categorias
- Ícones extraídos automaticamente dos executáveis
- Fecha ao clicar fora
- Instância única — sem janelas duplicadas
- Tela de configuração integrada

---

## Requisitos

- Windows 11
- Python 3.12+
- PySide6

```bash
pip install -r requirements.txt
```

---

## Instalação

```bash
git clone https://github.com/TitoBarrosTI/ex_t_bar.git
cd ex_t_bar
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Copie `config.example.json` para `config.json` e configure seus grupos e atalhos.

---

## Configuração

O arquivo `config.json` define os grupos e atalhos:

```json
{
    "groups": [
        {
            "name": "Dev",
            "shortcuts": [
                {"name": "VSCode", "path": "C:\\caminho\\para\\Code.exe"}
            ]
        }
    ]
}
```

Ou use a tela de configurações — clique no ícone ⚙ no popup.

---

## Uso

```bash
python main.py
```

Para uso permanente, empacote com PyInstaller e fixe o `.exe` na taskbar do Windows.

---

## Estrutura

```
ex_t_bar/
├── main.py            # Ponto de entrada, instância única
├── popup.py           # Janela popup com categorias e ícones
├── config_window.py   # Tela de configuração
├── config.py          # Leitura e escrita do config.json
├── winapi.py          # WinAPI: taskbar rect, DPI, extração de ícone
└── config.example.json
```

---

## Licença

MIT