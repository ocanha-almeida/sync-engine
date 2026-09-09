<#
.SYNOPSIS
Instalador do Sync Engine (Windows 10 / 11) - Modo Usuário
#>

param (
    [string]$Action = "install"
)

# 1. Instala direto na pasta do usuário (Sem precisar de Admin!)
$InstallDir = "$env:LOCALAPPDATA\sync-engine"
$TaskName = "SyncEngine_Background"

# 2. Rotina de Desinstalação
if ($Action -eq "uninstall") {
    Write-Host "🗑️  Desinstalando o Sync Engine do Windows..." -ForegroundColor Yellow
    schtasks /Delete /TN $TaskName /F *>$null
    Write-Host "✅ Serviço de fundo removido do Agendador de Tarefas." -ForegroundColor Green
    
    if (Test-Path $InstallDir) {
        Remove-Item -Recurse -Force $InstallDir
        Write-Host "✅ Diretório do programa removido ($InstallDir)." -ForegroundColor Green
    }
    
    $path = [Environment]::GetEnvironmentVariable("Path", [EnvironmentVariableTarget]::User)
    if ($path -like "*$InstallDir*") {
        $newPath = ($path -split ';' | Where-Object { $_ -ne$InstallDir }) -join ';'
        [Environment]::SetEnvironmentVariable("Path", $newPath, [EnvironmentVariableTarget]::User)
        Write-Host "✅ Variável de ambiente (PATH) do usuário limpa." -ForegroundColor Green
    }
    Write-Host "`nPressione Enter para sair..."
    Read-Host
    exit
}

# 3. Rotina de Instalação Normal
Write-Host "🚀 Iniciando a instalação do Sync Engine (Windows)..." -ForegroundColor Cyan

if (!(Test-Path $InstallDir)) {
    New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
}

Copy-Item -Path "$PSScriptRoot\*.py" -Destination $InstallDir -Force

$BatPath = Join-Path $InstallDir "sync-engine.cmd"
$BatContent = "@echo off`npython `"$InstallDir\sync_engine.py`" %*"
Set-Content -Path $BatPath -Value$BatContent -Encoding Ascii

Write-Host "✅ Arquivos copiados para $InstallDir" -ForegroundColor Green

$path = [Environment]::GetEnvironmentVariable("Path", [EnvironmentVariableTarget]::User)
if ($path -notlike "*$InstallDir*") {
    $newPath = $path + ";$InstallDir"
    [Environment]::SetEnvironmentVariable("Path", $newPath, [EnvironmentVariableTarget]::User)
    Write-Host "✅ Adicionado ao PATH do Usuário." -ForegroundColor Green
}

# 4. Encontra o caminho absoluto e exato do Pythonw no sistema do usuário
$PythonExe = (Get-Command python.exe -ErrorAction Stop).Source
$PythonwExe =$PythonExe -replace "python.exe", "pythonw.exe"

if (!(Test-Path $PythonwExe)) {
    Write-Warning "Aviso: pythonw.exe não localizado. Usando python.exe padrão."
    $PythonwExe =$PythonExe
}

# 5. Criar Tarefa Agendada no modo Usuário (Não pede elevação de UAC!)
Write-Host "⚙️  Configurando serviço invisível..." -ForegroundColor Cyan
$TaskArgs = "`"$InstallDir\sync_engine.py`""

# A tarefa agora força o uso do caminho absoluto garantindo que o programa nunca sofra com o erro de "Comando não reconhecido"
schtasks /Create /F /TN $TaskName /TR "`"$PythonwExe`" $TaskArgs" /SC ONLOGON *>$null

Write-Host "🎉 Instalação Concluída com Sucesso!" -ForegroundColor Green
Write-Host "💡 Limpeza recomendada: Você pode apagar manualmente a pasta antiga C:\opt\sync-engine se ela ainda existir." -ForegroundColor Yellow
Write-Host "`nFeche e abra um terminal novo para usar o comando 'sync-engine'."
Write-Host "Pressione Enter para sair..."
Read-Host