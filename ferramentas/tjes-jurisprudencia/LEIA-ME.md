# Jurisprudência do TJES direto da fonte (sem EmentAI)

Pequeno servidor que conecta o Claude à base oficial de jurisprudência do TJES
(`sistemas.tjes.jus.br/consulta-jurisprudencia`), consultando **somente acórdãos de 2º grau**
(Câmaras e Pleno; Turmas Recursais são excluídas), do mais recente ao mais antigo.

**Por que roda no seu computador:** o TJES (e o CNJ) só aceitam conexões vindas do Brasil.
Servidores do Claude na nuvem são bloqueados ("access from your country"). No seu computador,
com a sua internet, a consulta funciona normalmente. Não exige login, nem senha, nem chave.

## Requisitos
- **Claude Desktop** (aplicativo para Windows ou Mac) — https://claude.ai/download
- **Python 3.8+** — no Windows: https://www.python.org/downloads/ (marque **"Add python.exe to PATH"** na instalação)

## Instalação (Windows)

1. Crie a pasta `C:\tjes` e salve nela o arquivo **`tjes_mcp.py`** (desta pasta do repositório).
2. Teste no Prompt de Comando (`cmd`):
   ```
   python C:\tjes\tjes_mcp.py --teste "dano moral negativação indevida"
   ```
   Devem aparecer até 3 acórdãos com relator, data, link e ementa.
3. No Claude Desktop: **Configurações → Desenvolvedor → Editar configuração**. Abre o arquivo
   `claude_desktop_config.json`. Deixe assim (se já houver outros servidores, acrescente só o bloco `"tjes"`):
   ```json
   {
     "mcpServers": {
       "tjes": {
         "command": "python",
         "args": ["C:\\tjes\\tjes_mcp.py"]
       }
     }
   }
   ```
   Se `python` não for reconhecido, use `"command": "py"`.
4. Feche o Claude Desktop por completo (inclusive na bandeja do relógio) e abra de novo.
   No ícone de ferramentas da conversa devem aparecer **pesquisar_acordaos_tjes** e **obter_acordao_tjes**.

## Instalação (Mac)
Mesmos passos, salvando em `~/tjes/tjes_mcp.py`, testando com `python3`, e no JSON:
`"command": "python3", "args": ["/Users/SEU_USUARIO/tjes/tjes_mcp.py"]`.

## Uso
- "Pesquise no TJES acórdãos sobre dano moral por negativação indevida desde 2024"
- "Traga o inteiro teor do acórdão do processo 5011694-83.2023.8.08.0030"
- "Corrija esta minuta conforme o TJES" — a skill `corrigir-minuta-tjes` usa estas ferramentas
  primeiro e só recorre à EmentAI se elas não estiverem disponíveis.

## Observações
- Funciona apenas no Claude Desktop (e Claude Code) do computador onde foi instalado; no
  navegador/celular a skill continua usando a EmentAI.
- Base consultada: `pje2g` (acórdãos do PJe de 2º grau). Julgados anteriores ao PJe ficam na base
  `legado`, não incluída.
- Fonte técnica: API pública usada pelo próprio site do TJES, também documentada no projeto
  aberto `hebervalverde/mcp-consulta-processual-tjes` (licença MIT).
