# FactoryOps — Instalador da Tarefa Agendada do Sincronizador
#
# Execute este script como Administrador no PC da fabrica:
#   Clique direito > "Executar como administrador"
#
# O sincronizador sera iniciado ao LIGAR o PC, independente do usuario logado.
# Apenas uma instancia roda por vez (protecao contra duplicatas).

param(
    [string]$PythonwPath = ""
)

# ─── Verifica privilegio de administrador ─────────────────────────────────────
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host ""
    Write-Host "ERRO: Execute este script como Administrador." -ForegroundColor Red
    Write-Host "Clique direito no arquivo > Executar com PowerShell como administrador." -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Pressione Enter para sair"
    exit 1
}

Write-Host ""
Write-Host "FactoryOps — Instalador da Tarefa Agendada" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# ─── Localiza pythonw.exe ──────────────────────────────────────────────────────
if ($PythonwPath -and (Test-Path $PythonwPath)) {
    Write-Host "pythonw.exe informado: $PythonwPath" -ForegroundColor Green
} else {
    Write-Host "Localizando pythonw.exe..." -ForegroundColor Gray

    $candidatos = @(
        (Get-Command pythonw.exe -ErrorAction SilentlyContinue)?.Source,
        "C:\Python313\pythonw.exe",
        "C:\Python312\pythonw.exe",
        "C:\Python311\pythonw.exe",
        "C:\Python310\pythonw.exe",
        "C:\Python39\pythonw.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python313\pythonw.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python312\pythonw.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python311\pythonw.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python310\pythonw.exe"
    ) | Where-Object { $_ -and (Test-Path $_) }

    if ($candidatos) {
        $PythonwPath = $candidatos[0]
        Write-Host "Encontrado: $PythonwPath" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "pythonw.exe nao encontrado automaticamente." -ForegroundColor Yellow
        $PythonwPath = Read-Host "Informe o caminho completo para pythonw.exe (ex: C:\Python312\pythonw.exe)"
        if (-not (Test-Path $PythonwPath)) {
            Write-Host "Arquivo nao encontrado: $PythonwPath" -ForegroundColor Red
            Read-Host "Pressione Enter para sair"
            exit 1
        }
    }
}

# ─── Caminhos ─────────────────────────────────────────────────────────────────
$scriptDir  = Split-Path -Parent $MyInvocation.MyCommand.Path
$scriptPy   = Join-Path $scriptDir "sincronizador.py"
$envFile    = Join-Path $scriptDir ".env"
$nomeTarefa = "FactoryOps Sincronizador"

if (-not (Test-Path $scriptPy)) {
    Write-Host "ERRO: sincronizador.py nao encontrado em: $scriptDir" -ForegroundColor Red
    Read-Host "Pressione Enter para sair"
    exit 1
}

if (-not (Test-Path $envFile)) {
    Write-Host "AVISO: arquivo .env nao encontrado em $scriptDir" -ForegroundColor Yellow
    Write-Host "O sincronizador precisa do .env para funcionar." -ForegroundColor Yellow
    Write-Host "Copie .env.example para .env e preencha os valores antes de usar." -ForegroundColor Yellow
    Write-Host ""
}

# ─── Remove tarefa anterior se existir ────────────────────────────────────────
$existente = Get-ScheduledTask -TaskName $nomeTarefa -ErrorAction SilentlyContinue
if ($existente) {
    Write-Host "Removendo tarefa existente '$nomeTarefa'..." -ForegroundColor Gray
    Unregister-ScheduledTask -TaskName $nomeTarefa -Confirm:$false
}

# ─── Cria a tarefa ────────────────────────────────────────────────────────────
$action = New-ScheduledTaskAction `
    -Execute  $PythonwPath `
    -Argument "`"$scriptPy`"" `
    -WorkingDirectory $scriptDir

$trigger = New-ScheduledTaskTrigger -AtStartup

$principal = New-ScheduledTaskPrincipal `
    -UserId    "SYSTEM" `
    -LogonType ServiceAccount `
    -RunLevel  Highest

$settings = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit ([TimeSpan]::Zero) `
    -RestartCount       3 `
    -RestartInterval    (New-TimeSpan -Minutes 2) `
    -StartWhenAvailable $true `
    -MultipleInstances  IgnoreNew

Register-ScheduledTask `
    -TaskName   $nomeTarefa `
    -Action     $action `
    -Trigger    $trigger `
    -Principal  $principal `
    -Settings   $settings `
    -Description "Sincronizador automatico de producao FactoryOps. Inicia com o sistema." | Out-Null

# ─── Verifica se foi criada ───────────────────────────────────────────────────
$tarefa = Get-ScheduledTask -TaskName $nomeTarefa -ErrorAction SilentlyContinue
if ($tarefa) {
    Write-Host ""
    Write-Host "Tarefa '$nomeTarefa' instalada com sucesso!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Como funciona:" -ForegroundColor Cyan
    Write-Host "  - O sincronizador inicia automaticamente ao LIGAR o PC"
    Write-Host "  - Funciona para qualquer usuario logado"
    Write-Host "  - Apenas uma instancia roda por vez"
    Write-Host "  - Logs gravados em: $scriptDir\sincronizador.log"
    Write-Host ""
    Write-Host "Para iniciar agora sem reiniciar:" -ForegroundColor Yellow
    Write-Host "  Start-ScheduledTask -TaskName '$nomeTarefa'" -ForegroundColor Gray
    Write-Host ""
} else {
    Write-Host "ERRO: falha ao criar a tarefa agendada." -ForegroundColor Red
}

Read-Host "Pressione Enter para sair"
