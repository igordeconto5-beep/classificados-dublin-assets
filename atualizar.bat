@echo off
title Atualizando projeto...
cd /d "%~dp0"

echo.
echo ========================================
echo   Buscando atualizacoes do GitHub...
echo ========================================
echo.

git pull

echo.
echo ========================================
echo   Pronto! Projeto atualizado.
echo ========================================
echo.
pause
