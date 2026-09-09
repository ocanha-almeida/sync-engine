<#
.SYNOPSIS
Instalador do Sync Engine (Windows 10 / 11)
#>

param (
    [string]$Action = "install"
)

# 1. Checagem de Administrador (Pede permissÃ£o automaticamente)
if (!([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Warning "âš ï¸ Solicitando privilÃ©gios de Administrador..."
    Start-Process powershell.exe "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`" $Action" -Verb RunAs
    exit
}

# 2. VariÃ¡veis base
$InstallDir = "C:\opt\sync-engine"
$TaskName = "SyncEngine_Background"

# 3. Rotina de DesinstalaÃ§Ã£o
if ($Action -eq "uninstall") {
    Write-Host "ðŸ—‘ï¸  Desinstalando o Sync Engine do Windows..." -ForegroundColor Yellow
    
    schtasks /Delete /TN $TaskName /F *>$null
    Write-Host "âœ… ServiÃ§o de fundo removido do Agendador de Tarefas." -ForegroundColor Green
    
    if (Test-Path $InstallDir) {
        Remove-Item -Recurse -Force $InstallDir
        Write-Host "âœ… DiretÃ³rio do programa removido ($InstallDir)." -ForegroundColor Green
    }
    
    $path = [Environment]::GetEnvironmentVariable("Path", [EnvironmentVariableTarget]::Machine)
    if ($path -like "*$InstallDir*") {
        $newPath = ($path -split ';' | Where-Object { $_ -ne$InstallDir }) -join ';'
        [Environment]::SetEnvironmentVariable("Path", $newPath, [EnvironmentVariableTarget]::Machine)
        Write-Host "âœ… VariÃ¡vel de ambiente (PATH) do sistema limpa." -ForegroundColor Green
    }
    
    Write-Host "âš ï¸  Nota: Seus bancos de dados em ~/.config/sync_engine foram mantidos por seguranÃ§a." -ForegroundColor Cyan
    Write-Host "`nPressione Enter para sair..."
    Read-Host
    exit
}

# 4. Rotina de InstalaÃ§Ã£o Normal
Write-Host "ðŸš€ Iniciando a instalaÃ§Ã£o do Sync Engine (Windows)..." -ForegroundColor Cyan

if (!(Test-Path $InstallDir)) {
    New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
}

# Usa $PSScriptRoot para garantir que pega os .py da mesma pasta do script
Copy-Item -Path "$PSScriptRoot\*.py" -Destination $InstallDir -Force

# Cria o wrapper executÃ¡vel para terminal usando ASCII para evitar o bug do BOM
$BatPath = Join-Path $InstallDir "sync-engine.cmd"
$BatContent = "@echo off`npython `"$InstallDir\sync_engine.py`" %*"
Set-Content -Path $BatPath -Value$BatContent -Encoding Ascii

Write-Host "âœ… Arquivos e mÃ³dulos .py copiados para $InstallDir" -ForegroundColor Green

$path = [Environment]::GetEnvironmentVariable("Path", [EnvironmentVariableTarget]::Machine)
if ($path -notlike "*$InstallDir*") {
    $newPath = $path + ";$InstallDir"
    [Environment]::SetEnvironmentVariable("Path", $newPath, [EnvironmentVariableTarget]::Machine)
    Write-Host "âœ… Adicionado ao PATH do Sistema." -ForegroundColor Green
}

# 5. Criar Tarefa Agendada (Equivalente ao Systemd/Linger)
Write-Host "âš™ï¸  Configurando serviÃ§o contÃ­nuo de inicializaÃ§Ã£o (Task Scheduler)..." -ForegroundColor Cyan
$TaskCommand = "pythonw.exe"
$TaskArgs = "`"$InstallDir\sync_engine.py`""

schtasks /Create /F /TN $TaskName /TR "$TaskCommand $TaskArgs" /SC ONLOGON /RL HIGHEST *>$null

Write-Host "ðŸŽ‰ InstalaÃ§Ã£o ConcluÃ­da com Sucesso!" -ForegroundColor Green
Write-Host "ðŸ’¡ VocÃª jÃ¡ pode abrir um novo PowerShell ou CMD e digitar 'sync-engine'." -ForegroundColor Yellow
Write-Host "`nPressione Enter para sair..."
Read-Host<#
.SYNOPSIS
Instalador do Sync Engine (Windows 10 / 11)
#>

param (
    [string]$Action = "install"
)

# 1. Checagem de Administrador (Pede permissão automaticamente)
if (!([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Warning "? Solicitando privilégios de Administrador..."
    Start-Process powershell.exe "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`" $Action" -Verb RunAs
    exit
}

# 2. Variáveis base
$InstallDir = "C:\opt\sync-engine"
$TaskName = "SyncEngine_Background"

# 3. Rotina de Desinstalação
if ($Action -eq "uninstall") {
    Write-Host "?  Desinstalando o Sync Engine do Windows..." -ForegroundColor Yellow
    
    schtasks /Delete /TN $TaskName /F *>$null
    Write-Host "? Serviço de fundo removido do Agendador de Tarefas." -ForegroundColor Green
    
    if (Test-Path $InstallDir) {
        Remove-Item -Recurse -Force $InstallDir
        Write-Host "? Diretório do programa removido ($InstallDir)." -ForegroundColor Green
    }
    
    $path = [Environment]::GetEnvironmentVariable("Path", [EnvironmentVariableTarget]::Machine)
    if ($path -like "*$InstallDir*") {
        $newPath = ($path -split ';' | Where-Object { $_ -ne$InstallDir }) -join ';'
        [Environment]::SetEnvironmentVariable("Path", $newPath, [EnvironmentVariableTarget]::Machine)
        Write-Host "? Variável de ambiente (PATH) do sistema limpa." -ForegroundColor Green
    }
    
    Write-Host "?  Nota: Seus bancos de dados em ~/.config/sync_engine foram mantidos por segurança." -ForegroundColor Cyan
    Write-Host "`nPressione Enter para sair..."
    Read-Host
    exit
}

# 4. Rotina de Instalação Normal
Write-Host "? Iniciando a instalação do Sync Engine (Windows)..." -ForegroundColor Cyan

if (!(Test-Path $InstallDir)) {
    New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
}

# Usa $PSScriptRoot para garantir que pega os .py da mesma pasta do script
Copy-Item -Path "$PSScriptRoot\*.py" -Destination $InstallDir -Force

# Cria o wrapper executável para terminal usando ASCII para evitar o bug do BOM
$BatPath = Join-Path $InstallDir "sync-engine.cmd"
$BatContent = "@echo off`npython `"$InstallDir\sync_engine.py`" %*"
Set-Content -Path $BatPath -Value$BatContent -Encoding Ascii

Write-Host "? Arquivos e módulos .py copiados para $InstallDir" -ForegroundColor Green

$path = [Environment]::GetEnvironmentVariable("Path", [EnvironmentVariableTarget]::Machine)
if ($path -notlike "*$InstallDir*") {
    $newPath = $path + ";$InstallDir"
    [Environment]::SetEnvironmentVariable("Path", $newPath, [EnvironmentVariableTarget]::Machine)
    Write-Host "? Adicionado ao PATH do Sistema." -ForegroundColor Green
}

# 5. Criar Tarefa Agendada (Equivalente ao Systemd/Linger)
Write-Host "?  Configurando serviço contínuo de inicialização (Task Scheduler)..." -ForegroundColor Cyan
$TaskCommand = "pythonw.exe"
$TaskArgs = "`"$InstallDir\sync_engine.py`""

schtasks /Create /F /TN $TaskName /TR "$TaskCommand $TaskArgs" /SC ONLOGON /RL HIGHEST *>$null

Write-Host "? Instalação Concluída com Sucesso!" -ForegroundColor Green
Write-Host "? Você já pode abrir um novo PowerShell ou CMD e digitar 'sync-engine'." -ForegroundColor Yellow
Write-Host "`nPressione Enter para sair..."
Read-Host