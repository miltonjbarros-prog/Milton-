#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Servidor MCP local: jurisprudência do TJES (acórdãos de 2º grau).

Consulta direto a API pública de jurisprudência do TJES
(https://sistemas.tjes.jus.br/consulta-jurisprudencia/), a mesma usada pelo site.
O TJES só responde a conexões do Brasil, por isso este servidor roda no SEU
computador (Claude Desktop ou Claude Code local), e não na nuvem.

Ferramentas expostas ao Claude:
  - pesquisar_acordaos_tjes(consulta, quantidade, desde)
  - obter_acordao_tjes(numero_processo)

Somente biblioteca padrão do Python 3.8+. Apenas leitura (GET), sem login.

Teste rápido, sem o Claude:
  python tjes_mcp.py --teste "dano moral negativação indevida"
"""

import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

API = os.environ.get("TJES_API", "https://sistemas.tjes.jus.br/consulta-jurisprudencia/api")
CORE = "pje2g"  # acórdãos de 2º grau (PJe)
LINK = "https://sistemas.tjes.jus.br/consulta-jurisprudencia/#id={id}&core=pje2g"

# Órgãos que NÃO são segundo grau propriamente dito (Juizados).
EXCLUIR = re.compile(r"TURMA\s+RECURSAL|COLEGIADO\s+RECURSAL|JUIZADO|RECURSO\s+INOMINADO", re.I)


def log(msg):
    print(f"[tjes-jurisprudencia] {msg}", file=sys.stderr, flush=True)


# ---------------------------------------------------------------------------
# Acesso à API do TJES
# ---------------------------------------------------------------------------
def _get(params, timeout=60):
    url = API.rstrip("/") + "/search?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (tjes-jurisprudencia-mcp)",
        "Accept": "application/json",
    })
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def buscar(q, por_pagina=30, pagina=1):
    """Busca no core pje2g, tentando ordenar do mais recente; sem ordenação se a API recusar."""
    base = {"core": CORE, "q": q, "page": pagina, "per_page": por_pagina}
    for sort in ("dt_juntada desc", None):
        p = dict(base)
        if sort:
            p["sort"] = sort
        try:
            return _get(p)
        except urllib.error.HTTPError as e:
            if sort and e.code in (400, 422, 500):
                continue
            raise
    return {"docs": [], "total": 0}


def _txt(v):
    if isinstance(v, list):
        v = " ".join(str(x) for x in v)
    return " ".join(str(v or "").split())


def _data(d):
    for k in ("dt_julgamento", "dt_juntada", "dt_publicacao"):
        if d.get(k):
            return str(d[k])[:10]
    return "?"


def _segundo_grau(d):
    campos = " ".join(_txt(d.get(k)) for k in ("orgao_julgador", "classe_judicial", "orgao"))
    return not EXCLUIR.search(campos)


def _ementa(d):
    return _txt(d.get("ementa") or d.get("acordao") or d.get("inteiro_teor") or "")


def _cabecalho(d):
    return (f"Processo {d.get('nr_processo', '?')} | {_txt(d.get('classe_judicial'))}\n"
            f"Relator(a): {_txt(d.get('magistrado')) or '?'} | "
            f"Órgão: {_txt(d.get('orgao_julgador')) or '?'} | Data: {_data(d)}\n"
            f"Link oficial: {LINK.format(id=d.get('id', ''))}")


# ---------------------------------------------------------------------------
# Ferramentas
# ---------------------------------------------------------------------------
def pesquisar_acordaos_tjes(consulta, quantidade=8, desde=None):
    quantidade = max(1, min(int(quantidade or 8), 20))
    r = buscar(consulta, por_pagina=min(quantidade * 3, 60))
    docs = [d for d in r.get("docs", []) if _segundo_grau(d)]
    if desde:
        docs = [d for d in docs if _data(d) >= str(desde)[:10]]
    docs.sort(key=_data, reverse=True)
    docs = docs[:quantidade]
    out = [f"TJES - acórdãos de 2º grau | consulta: {consulta!r} | "
           f"{r.get('total', '?')} no índice | exibindo {len(docs)} (Turmas Recursais excluídas)", ""]
    for i, d in enumerate(docs, 1):
        out += [f"[{i}] " + _cabecalho(d), "EMENTA: " + (_ementa(d)[:3000] or "(sem ementa)"), ""]
    if not docs:
        out.append("Nenhum acórdão de 2º grau encontrado. Tente outros termos.")
    return "\n".join(out)


def obter_acordao_tjes(numero_processo):
    dig = re.sub(r"\D", "", numero_processo)
    if len(dig) == 20:
        nro = f"{dig[0:7]}-{dig[7:9]}.{dig[9:13]}.{dig[13]}.{dig[14:16]}.{dig[16:20]}"
    else:
        nro = numero_processo.strip()
    r = buscar(f'nr_processo:"{nro}"', por_pagina=50)
    docs = [d for d in r.get("docs", [])
            if re.sub(r"\D", "", str(d.get("nr_processo", ""))) == dig or len(dig) != 20]
    if not docs:
        return f"Nenhum acórdão de 2º grau encontrado para {nro}."
    out = []
    for d in docs:
        texto = _txt(d.get("inteiro_teor") or d.get("acordao") or d.get("ementa"))
        out += ["=" * 70, _cabecalho(d),
                "ATENÇÃO: órgão de Juizado/Turma Recursal." if not _segundo_grau(d) else "",
                "=" * 70, texto[:60000], ""]
    return "\n".join(out)


FERRAMENTAS = [
    {
        "name": "pesquisar_acordaos_tjes",
        "description": ("Pesquisa ACÓRDÃOS DE 2º GRAU do TJES (Câmaras e Pleno), direto na base "
                        "oficial do Tribunal, do mais recente ao mais antigo, excluindo Turmas "
                        "Recursais. Retorna processo, relator, órgão, data, link oficial e ementa. "
                        "Aceita palavras-chave ou sintaxe Solr (ex.: \"dano moral\" AND negativação)."),
        "inputSchema": {
            "type": "object",
            "properties": {
                "consulta": {"type": "string", "description": "Tema ou palavras-chave"},
                "quantidade": {"type": "integer", "description": "1 a 20 (padrão 8)"},
                "desde": {"type": "string", "description": "Data mínima AAAA-MM-DD (opcional)"},
            },
            "required": ["consulta"],
        },
    },
    {
        "name": "obter_acordao_tjes",
        "description": "Retorna o inteiro teor do(s) acórdão(s) de 2º grau do TJES de um processo (número CNJ).",
        "inputSchema": {
            "type": "object",
            "properties": {"numero_processo": {"type": "string"}},
            "required": ["numero_processo"],
        },
    },
]


def executar(nome, a):
    if nome == "pesquisar_acordaos_tjes":
        return pesquisar_acordaos_tjes(a["consulta"], a.get("quantidade", 8), a.get("desde"))
    if nome == "obter_acordao_tjes":
        return obter_acordao_tjes(a["numero_processo"])
    raise ValueError(f"Ferramenta desconhecida: {nome}")


# ---------------------------------------------------------------------------
# Protocolo MCP (stdio, JSON-RPC 2.0, uma mensagem por linha)
# ---------------------------------------------------------------------------
def _responder(id_, resultado=None, erro=None):
    msg = {"jsonrpc": "2.0", "id": id_}
    msg["error" if erro else "result"] = erro or resultado
    sys.stdout.write(json.dumps(msg, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def main():
    try:
        sys.stdin.reconfigure(encoding="utf-8")
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass
    log("iniciado")
    for linha in sys.stdin:
        if not linha.strip():
            continue
        try:
            req = json.loads(linha)
        except ValueError:
            continue
        metodo, id_, params = req.get("method"), req.get("id"), req.get("params") or {}
        if metodo == "initialize":
            _responder(id_, {"protocolVersion": params.get("protocolVersion", "2025-06-18"),
                             "capabilities": {"tools": {}},
                             "serverInfo": {"name": "tjes-jurisprudencia", "version": "1.0.0"}})
        elif metodo == "tools/list":
            _responder(id_, {"tools": FERRAMENTAS})
        elif metodo == "tools/call":
            try:
                texto = executar(params.get("name"), params.get("arguments") or {})
                _responder(id_, {"content": [{"type": "text", "text": texto}]})
            except Exception as e:  # noqa: BLE001
                _responder(id_, {"content": [{"type": "text", "text": f"Erro: {e}"}], "isError": True})
        elif metodo == "ping":
            _responder(id_, {})
        elif id_ is not None and not str(metodo).startswith("notifications/"):
            _responder(id_, erro={"code": -32601, "message": f"Método não suportado: {metodo}"})


def instalar():
    """Copia este arquivo para ~/tjes e registra o servidor no Claude Desktop."""
    import glob
    import shutil
    destino_dir = os.path.join(os.path.expanduser("~"), "tjes")
    os.makedirs(destino_dir, exist_ok=True)
    destino = os.path.join(destino_dir, "tjes_mcp.py")
    origem = os.path.abspath(__file__)
    if os.path.normcase(origem) != os.path.normcase(destino):
        shutil.copyfile(origem, destino)
    print(f"1) Servidor copiado para: {destino}")

    if sys.platform == "win32":
        appdata = os.environ.get("APPDATA", "")
        local = os.environ.get("LOCALAPPDATA", "")
        pastas = [os.path.join(appdata, "Claude")]
        # versão do Claude instalada pela Microsoft Store
        pastas += glob.glob(os.path.join(local, "Packages", "Claude_*", "LocalCache", "Roaming", "Claude"))
    elif sys.platform == "darwin":
        pastas = [os.path.expanduser("~/Library/Application Support/Claude")]
    else:
        pastas = [os.path.expanduser("~/.config/Claude")]
    existentes = [p for p in pastas if os.path.isdir(p)] or pastas[:1]

    for pasta in existentes:
        os.makedirs(pasta, exist_ok=True)
        cfg = os.path.join(pasta, "claude_desktop_config.json")
        dados = {}
        if os.path.exists(cfg):
            shutil.copyfile(cfg, cfg + ".backup")
            try:
                with open(cfg, encoding="utf-8") as f:
                    dados = json.load(f) or {}
            except ValueError:
                print(f"   AVISO: {cfg} estava inválido; uma cópia ficou em .backup")
                dados = {}
        dados.setdefault("mcpServers", {})["tjes"] = {"command": sys.executable, "args": [destino]}
        with open(cfg, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        print(f"2) Claude Desktop configurado em: {cfg}")

    print("3) Testando a conexão com o TJES...\n")
    try:
        print(pesquisar_acordaos_tjes("dano moral negativação indevida", 2))
        print("\nTUDO CERTO! Feche o Claude Desktop por completo e abra de novo.")
    except Exception as e:  # noqa: BLE001
        print(f"FALHA NO TESTE: {e}\nCopie esta mensagem e envie ao Claude.")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "--instalar":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:  # noqa: BLE001
            pass
        instalar()
    elif len(sys.argv) >= 3 and sys.argv[1] == "--teste":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:  # noqa: BLE001
            pass
        print(pesquisar_acordaos_tjes(" ".join(sys.argv[2:]), 3))
    else:
        main()
