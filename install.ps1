<#
.SYNOPSIS
Instalador do Sync Engine (Windows 10 / 11) - Modo Usuário
#>

param (
    [string]$Action = "install"
)

$InstallDir = "$env:LOCALAPPDATA\sync-engine"
$TaskName = "SyncEngine_Background"

if ($Action -eq "uninstall") {
    Write-Host "🗑️  Desinstalando o Sync Engine do Windows..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
    Write-Host "✅ Serviço de fundo removido do Agendador de Tarefas." -ForegroundColor Green
    
    if (Test-Path $InstallDir) {
        Remove-Item -Recurse -Force $InstallDir
        Write-Host "✅ Diretório do programa removido ($InstallDir)." -ForegroundColor Green
    }
    
    $path = [Environment]::GetEnvironmentVariable("Path", [EnvironmentVariableTarget]::User)
    if ($path -like "*$InstallDir*") {
        $newPath = ($path -split ';' | Where-Object { $_ -ne $InstallDir }) -join ';'
        [Environment]::SetEnvironmentVariable("Path", $newPath, [EnvironmentVariableTarget]::User)
        Write-Host "✅ Variável de ambiente (PATH) do usuário limpa." -ForegroundColor Green
    }
    Write-Host "`nPressione Enter para sair..."
    Read-Host
    exit
}

Write-Host "🚀 Iniciando a instalação do Sync Engine (Windows)..." -ForegroundColor Cyan

if (!(Test-Path $InstallDir)) {
    New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
}

Copy-Item -Path "$PSScriptRoot\*.py" -Destination $InstallDir -Force

$BatPath = Join-Path $InstallDir "sync-engine.cmd"
$BatContent = "@echo off`npython `"$InstallDir\sync_engine.py`" %*"
Set-Content -Path $BatPath -Value $BatContent -Encoding Ascii

Write-Host "✅ Arquivos copiados para $InstallDir" -ForegroundColor Green

$path = [Environment]::GetEnvironmentVariable("Path", [EnvironmentVariableTarget]::User)
if ($path -notlike "*$InstallDir*") {
    $newPath = $path + ";$InstallDir"
    [Environment]::SetEnvironmentVariable("Path", $newPath, [EnvironmentVariableTarget]::User)
    Write-Host "✅ Adicionado ao PATH do Usuário." -ForegroundColor Green
}

Write-Host "⚙️  Configurando serviço invisível para o usuário: $env:USERNAME..." -ForegroundColor Cyan

# Usamos PowerShell oculto para chamar o Python. Isso evita a quebra do pythonw e permite capturar os erros críticos (crashes).
$ActionTask = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-WindowStyle Hidden -NoProfile -ExecutionPolicy Bypass -Command `"python '$InstallDir\sync_engine.py' *>> '$InstallDir\background_crash.log'`""
$TriggerTask = New-ScheduledTaskTrigger -AtLogOn
$PrincipalTask = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive
$SettingsTask = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

Register-ScheduledTask -TaskName $TaskName -Action $ActionTask -Trigger $TriggerTask -Principal $PrincipalTask -Settings $SettingsTask -Force *>$null

Write-Host "🎉 Instalação Concluída com Sucesso!" -ForegroundColor Green
Write-Host "`nFeche e abra um terminal novo para usar o comando 'sync-engine'."
Write-Host "Pressione Enter para sair..."
Read-Host