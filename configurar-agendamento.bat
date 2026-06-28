@echo off
title Configurando atualizacao automatica...
cd /d "%~dp0"

echo.
echo ========================================
echo   Configurando atualizacao automatica
echo ========================================
echo.
echo O projeto sera atualizado automaticamente
echo toda vez que voce ligar o computador.
echo.

set SCRIPT="%~dp0atualizar-silencioso.bat"
set TASKNAME="Atualizar Classificados Dublin"

schtasks /create /tn %TASKNAME% /tr %SCRIPT% /sc ONLOGON /ru "%USERNAME%" /f

if %ERRORLEVEL% == 0 (
    echo.
    echo ========================================
    echo   Pronto! Agendamento configurado.
    echo ========================================
    echo.
    echo A partir de agora, o projeto sera
    echo atualizado automaticamente ao ligar.
) else (
    echo.
    echo Erro ao configurar. Tente executar
    echo este arquivo como Administrador.
    echo (clique direito - Executar como admin)
)

echo.
pause
