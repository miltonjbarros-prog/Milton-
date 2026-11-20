@echo off
chcp 65001 >nul
title Instalador - Jurisprudencia TJES para o Claude
cd /d "%~dp0"
echo.
echo  Instalando o acesso a jurisprudencia do TJES no Claude Desktop...
echo.
if not exist "tjes_mcp.py" (
  echo  ERRO: o arquivo tjes_mcp.py precisa estar na mesma pasta deste instalador.
  goto fim
)
set PY=
where py >nul 2>nul && set PY=py
if "%PY%"=="" where python >nul 2>nul && set PY=python
if "%PY%"=="" (
  echo  ERRO: Python nao encontrado.
  echo  Instale em https://www.python.org/downloads/ marcando "Add python.exe to PATH"
  echo  e depois rode este instalador de novo.
  goto fim
)
%PY% tjes_mcp.py --instalar
:fim
echo.
pause
