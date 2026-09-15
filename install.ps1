param (
    [string]$Action = "install"
)

$InstallDir = "$env:LOCALAPPDATA\sync-engine"
$StartupFolder = [Environment]::GetFolderPath('Startup')
$ShortcutPath = Join-Path $StartupFolder "SyncEngine.lnk"

if ($Action -eq "uninstall") {
    Write-Host "🗑️ Desinstalando..." -ForegroundColor Yellow
    
    # Força a parada do processo se estiver rodando
    Stop-Process -Name "pythonw" -ErrorAction SilentlyContinue
    
    if (Test-Path $ShortcutPath) { Remove-Item $ShortcutPath -Force }
    if (Test-Path $InstallDir) { Remove-Item -Recurse -Force $InstallDir }
    
    $path = [Environment]::GetEnvironmentVariable("Path", [EnvironmentVariableTarget]::User)
    if ($path -like "*$InstallDir*") {
        $newPath = ($path -split ';' | Where-Object { $_ -ne $InstallDir }) -join ';'
        [Environment]::SetEnvironmentVariable("Path", $newPath, [EnvironmentVariableTarget]::User)
    }
    Write-Host "✅ Removido com sucesso. Pressione Enter para sair." -ForegroundColor Green
    Read-Host
    exit
}

Write-Host "🚀 Instalando Sync Engine (Modo Startup)..." -ForegroundColor Cyan
if (!(Test-Path $InstallDir)) { New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null }

Copy-Item -Path "$PSScriptRoot\*.py" -Destination $InstallDir -Force

$BatPath = Join-Path $InstallDir "sync-engine.cmd"
$BatContent = "@echo off`npython `"$InstallDir\sync_engine.py`" %*"
Set-Content -Path $BatPath -Value $BatContent -Encoding Ascii

$path = [Environment]::GetEnvironmentVariable("Path", [EnvironmentVariableTarget]::User)
if ($path -notlike "*$InstallDir*") {
    $newPath = $path + ";$InstallDir"
    [Environment]::SetEnvironmentVariable("Path", $newPath, [EnvironmentVariableTarget]::User)
}

$PythonExe = (Get-Command python.exe -ErrorAction Stop).Source
$PythonwExe = $PythonExe -replace "python.exe", "pythonw.exe"
if (!(Test-Path $PythonwExe)) { $PythonwExe = $PythonExe }

# Criação do Atalho na Pasta de Inicialização
Write-Host "⚙️ Configurando inicialização automática..." -ForegroundColor Cyan
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $PythonwExe
$Shortcut.Arguments = "`"$InstallDir\sync_engine.py`""
$Shortcut.WorkingDirectory = $InstallDir
$Shortcut.WindowStyle = 7
$Shortcut.Save()

Write-Host "🎉 Instalação Concluída!" -ForegroundColor Green
Write-Host "Feche este terminal. Pressione Enter para sair."
Read-Host