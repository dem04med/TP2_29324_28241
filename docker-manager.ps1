# Script PowerShell para facilitar o uso do Docker Compose no Windows

param(
    [Parameter(Position=0)]
    [string]$Command = ""
)

Write-Host "=== Configuração Docker XML-RPC Server ===" -ForegroundColor Green
Write-Host

function Show-Help {
    Write-Host "Uso: .\docker-manager.ps1 [comando]" -ForegroundColor Yellow
    Write-Host
    Write-Host "Comandos disponíveis:" -ForegroundColor Cyan
    Write-Host "  build     - Constrói as imagens Docker"
    Write-Host "  start     - Inicia os serviços"
    Write-Host "  stop      - Para os serviços"  
    Write-Host "  restart   - Reinicia os serviços"
    Write-Host "  logs      - Mostra logs dos serviços"
    Write-Host "  status    - Mostra status dos containers"
    Write-Host "  clean     - Remove containers e volumes"
    Write-Host "  test      - Executa clientes de teste (XML-RPC + GraphQL)"
    Write-Host "  graphql   - Testa apenas GraphQL com exemplos"
    Write-Host "  db        - Conecta ao PostgreSQL"
    Write-Host "  help      - Mostra esta ajuda"
    Write-Host
}

function Test-DockerCompose {
    if (-not (Get-Command docker-compose -ErrorAction SilentlyContinue)) {
        Write-Host "Erro: docker-compose não está instalado." -ForegroundColor Red
        Write-Host "Instale o Docker Desktop primeiro." -ForegroundColor Red
        exit 1
    }
}

function Build-Images {
    Write-Host "Construindo imagens Docker..." -ForegroundColor Yellow
    docker-compose build
}

function Start-Services {
    Write-Host "Iniciando serviços..." -ForegroundColor Yellow
    docker-compose up -d
    Write-Host
    Write-Host "Aguardando inicialização dos serviços..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
    
    Write-Host "Status dos containers:" -ForegroundColor Green
    docker-compose ps
    Write-Host
    Write-Host "Servidor XML-RPC disponível em: http://localhost:8000" -ForegroundColor Green
    Write-Host "PostgreSQL disponível em: localhost:5432" -ForegroundColor Green
}

function Stop-Services {
    Write-Host "Parando serviços..." -ForegroundColor Yellow
    docker-compose down
}

function Restart-Services {
    Write-Host "Reiniciando serviços..." -ForegroundColor Yellow
    docker-compose restart
}

function Show-Logs {
    Write-Host "Logs dos serviços (Ctrl+C para sair):" -ForegroundColor Yellow
    docker-compose logs -f
}

function Show-Status {
    Write-Host "Status dos containers:" -ForegroundColor Green
    docker-compose ps
    Write-Host
    
    Write-Host "Serviços disponíveis:" -ForegroundColor Green
    Write-Host "  🔌 XML-RPC Server: http://localhost:8000" -ForegroundColor Cyan
    Write-Host "  🌐 GraphQL Server: http://localhost:5000/graphql" -ForegroundColor Cyan
    Write-Host "  🎮 GraphiQL Interface: http://localhost:5000/graphql" -ForegroundColor Cyan
    Write-Host "  🗄️ PostgreSQL: localhost:5432" -ForegroundColor Cyan
    Write-Host
    
    Write-Host "Uso de recursos:" -ForegroundColor Green
    $containers = docker-compose ps -q
    if ($containers) {
        docker stats --no-stream $containers
    } else {
        Write-Host "Nenhum container em execução" -ForegroundColor Yellow
    }
}

function Clean-All {
    Write-Host "Parando e removendo containers..." -ForegroundColor Yellow
    docker-compose down -v --remove-orphans
    
    Write-Host "Removendo imagens..." -ForegroundColor Yellow
    docker-compose down --rmi all
    
    Write-Host "Removendo volumes não utilizados..." -ForegroundColor Yellow
    docker volume prune -f
    
    Write-Host "Limpeza concluída." -ForegroundColor Green
}

function Run-TestClient {
    Write-Host "Executando clientes de teste..." -ForegroundColor Yellow
    
    Write-Host "📡 Testando XML-RPC Server..." -ForegroundColor Cyan
    docker-compose exec xmlrpc_server python test_client.py
    
    Write-Host "`n🌐 Testando GraphQL Server..." -ForegroundColor Cyan
    docker-compose exec graphql_server python test_graphql_client.py
}

function Connect-Database {
    Write-Host "Conectando ao PostgreSQL..." -ForegroundColor Yellow
    docker-compose exec db psql -U user -d xmlrpc_db
}

# Processar comando
switch ($Command.ToLower()) {
    "build" {
        Test-DockerCompose
        Build-Images
    }
    "start" {
        Test-DockerCompose
        Start-Services
    }
    "stop" {
        Test-DockerCompose
        Stop-Services
    }
    "restart" {
        Test-DockerCompose
        Restart-Services
    }
    "logs" {
        Test-DockerCompose
        Show-Logs
    }
    "status" {
        Test-DockerCompose
        Show-Status
    }
    "clean" {
        Test-DockerCompose
        $confirm = Read-Host "Tem certeza que deseja remover todos os containers e dados? (y/N)"
        if ($confirm -match "^[Yy]$") {
            Clean-All
        } else {
            Write-Host "Operação cancelada." -ForegroundColor Yellow
        }
    }
    "test" {
        Test-DockerCompose
        Run-TestClient
    }
    "graphql" {
        Test-DockerCompose
        Write-Host "🌐 Testando GraphQL com exemplos..." -ForegroundColor Yellow
        docker-compose exec graphql_server python test_graphql_client.py examples
        Write-Host "`n🎮 Acesse GraphiQL em: http://localhost:5000/graphql" -ForegroundColor Green
    }
    "db" {
        Test-DockerCompose
        Connect-Database
    }
    { $_ -in "help", "--help", "-h" } {
        Show-Help
    }
    "" {
        Write-Host "Nenhum comando especificado." -ForegroundColor Yellow
        Write-Host
        Show-Help
    }
    default {
        Write-Host "Comando inválido: $Command" -ForegroundColor Red
        Write-Host
        Show-Help
        exit 1
    }
}