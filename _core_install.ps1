param (
    [string]$Action = "install"
)

try {
    $InstallDir = "$env:LOCALAPPDATA\sync-engine"
    $StartupFolder = [Environment]::GetFolderPath('Startup')
    $ShortcutPath = Join-Path $StartupFolder "SyncEngine.lnk"

    if ($Action -eq "uninstall") {
        Write-Host "🗑️ Starting Sync Engine removal..." -ForegroundColor Yellow
        Write-Host "   Iniciando a desinstalação..." -ForegroundColor Yellow
        
        Stop-Process -Name "pythonw" -ErrorAction SilentlyContinue
        
        if (Test-Path -LiteralPath $ShortcutPath) { Remove-Item -LiteralPath $ShortcutPath -Force }
        if (Test-Path -LiteralPath $InstallDir) { Remove-Item -LiteralPath $InstallDir -Recurse -Force }
        
        $path = [Environment]::GetEnvironmentVariable("Path", [EnvironmentVariableTarget]::User)
        if ($path -like "*$InstallDir*") {
            $newPath = ($path -split ';' | Where-Object { $_ -ne $InstallDir }) -join ';'
            [Environment]::SetEnvironmentVariable("Path", $newPath, [EnvironmentVariableTarget]::User)
        }
        Write-Host "✅ Successfully removed." -ForegroundColor Green
        Write-Host "   Removido com sucesso." -ForegroundColor Green
        Write-Host ""
        Read-Host "Press Enter to exit... / Pressione Enter para sair..."
        exit
    }

    Write-Host "🚀 Installing Sync Engine (Startup Mode)..." -ForegroundColor Cyan
    Write-Host "   Instalando Sync Engine (Modo Startup)..." -ForegroundColor Cyan

    if (!(Test-Path -LiteralPath $InstallDir)) { 
        New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null 
    }

    # Copia os arquivos Python de forma blindada
    Get-ChildItem -LiteralPath $PSScriptRoot -Filter "*.py" | Copy-Item -Destination $InstallDir -Force

    # Copia a pasta locales de forma blindada
    $SourceLocales = Join-Path $PSScriptRoot "locales"
    $DestLocales = Join-Path $InstallDir "locales"
    if (Test-Path -LiteralPath $SourceLocales) { 
        if (!(Test-Path -LiteralPath $DestLocales)) { 
            New-Item -ItemType Directory -Force -Path $DestLocales | Out-Null 
        }
        Get-ChildItem -LiteralPath $SourceLocales | Copy-Item -Destination $DestLocales -Recurse -Force 
    }

    # Criação do .cmd corrigida
    $BatPath = Join-Path $InstallDir "sync-engine.cmd"
    $BatContent = "@echo off`npython `"$InstallDir\sync_engine.py`" %*"
    Set-Content -LiteralPath $BatPath -Value $BatContent -Encoding Ascii

    # Atualização da Variável de Ambiente (PATH)
    $path = [Environment]::GetEnvironmentVariable("Path", [EnvironmentVariableTarget]::User)
    if ($path -notlike "*$InstallDir*") {
        $newPath = $path + ";$InstallDir"
        [Environment]::SetEnvironmentVariable("Path", $newPath, [EnvironmentVariableTarget]::User)
    }

    # Verifica se o Python existe no sistema de forma segura
    try {
        $PythonExe = (Get-Command python.exe -ErrorAction Stop).Source
    } catch {
        Write-Host "`n❌ ERRO CRÍTICO: O Python não foi encontrado no seu sistema!" -ForegroundColor Red
        Write-Host "Por favor, instale o Python e certifique-se de marcar a caixa 'Add python.exe to PATH' na primeira tela do instalador." -ForegroundColor Yellow
        Read-Host "Pressione Enter para sair..."
        exit
    }

    $PythonwExe = $PythonExe -replace "python.exe", "pythonw.exe"
    if (!(Test-Path -LiteralPath $PythonwExe)) { $PythonwExe = $PythonExe }

    Write-Host "⚙️ Configuring automatic startup..." -ForegroundColor Cyan
    Write-Host "   Configurando inicialização automática..." -ForegroundColor Cyan
    $WshShell = New-Object -comObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut($ShortcutPath)
    $Shortcut.TargetPath = $PythonwExe
    $Shortcut.Arguments = "`"$InstallDir\sync_engine.py`""
    $Shortcut.WorkingDirectory = $InstallDir
    $Shortcut.WindowStyle = 7
    $Shortcut.Save()

    Write-Host "🎉 Installation Complete!" -ForegroundColor Green
    Write-Host "   Instalação Concluída!" -ForegroundColor Green
    Write-Host ""
    
} catch {
    Write-Host "`n❌ ERRO DURANTE A INSTALAÇÃO:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}

Read-Host "Close this terminal. Press Enter to exit... / Feche este terminal. Pressione Enter para sair..."
