#!/bin/bash

set -e

INSTALL_DIR="$(pwd)/.install_status"
mkdir -p "$INSTALL_DIR"

clear

echo "========================================================="
echo "  🚀 Bem-vindo ao Instalador do Projeto Lineage 2 PDL!   "
echo "========================================================="
echo

if [ -f "$INSTALL_DIR/.install_done" ]; then
  echo "⚠️  Instalação já foi concluída anteriormente."
  echo
  read -p "Deseja rodar os containers (s) ou refazer a instalação (r)? (s/r): " OPCAO

  if [[ "$OPCAO" == "s" || "$OPCAO" == "S" ]]; then
    pushd lineage > /dev/null
    docker compose up -d
    popd > /dev/null
    echo "✅ Containers iniciados."
    exit 0
  elif [[ "$OPCAO" == "r" || "$OPCAO" == "R" ]]; then
    echo "🔄 Refazendo instalação..."
    rm -rf "$INSTALL_DIR"
    mkdir -p "$INSTALL_DIR"
  else
    echo "❌ Opção inválida."
    exit 1
  fi
fi

echo "Este script vai preparar todo o ambiente para você."
echo
read -p "Deseja continuar com a instalação? (s/n): " CONTINUE

if [[ "$CONTINUE" != "s" && "$CONTINUE" != "S" ]]; then
  echo "Instalação cancelada."
  exit 0
fi

if ! command -v git &> /dev/null; then
  echo "❌ Git não está instalado. Instalando..."
  sudo apt install -y git
fi

if [ ! -f "$INSTALL_DIR/system_ready" ]; then
  echo
  echo "🔄 Atualizando pacotes e instalando dependências..."
  sudo apt update && sudo apt upgrade -y
  sudo apt install -y apt-transport-https ca-certificates curl software-properties-common python3-venv python3-pip gettext
  touch "$INSTALL_DIR/system_ready"
fi

if [ ! -f "$INSTALL_DIR/docker_ready" ]; then
  echo
  echo "🐳 Instalando Docker e Docker Compose..."
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
  sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu jammy stable"
  sudo apt update
  sudo apt install -y docker-ce
  sudo systemctl enable docker
  sudo systemctl start docker

  if ! docker info &> /dev/null; then
    echo "❌ Docker não está rodando corretamente. Verifique a instalação."
    exit 1
  fi

  if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose não encontrado. Instalando versão standalone..."
    sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    docker-compose --version
  else
    docker compose version
  fi

  touch "$INSTALL_DIR/docker_ready"
fi

if [ ! -f "$INSTALL_DIR/repo_cloned" ]; then
  echo
  echo "📂 Clonando repositório do projeto..."
  git clone https://github.com/jrompani/lineage.git || true
  touch "$INSTALL_DIR/repo_cloned"
fi

pushd lineage > /dev/null

if [ ! -f "$INSTALL_DIR/python_ready" ]; then
  echo
  echo "🐍 Configurando ambiente Python (virtualenv)..."
  python3 -m venv .venv
  source .venv/bin/activate
  pip install --upgrade pip
  pip install -r requirements.txt
  mkdir -p logs
  touch "$INSTALL_DIR/python_ready"
else
  source .venv/bin/activate
fi

if [ ! -f "$INSTALL_DIR/env_created" ]; then
  echo
  echo "⚙️ Criando arquivo .env (se não existir)..."
  if [ ! -f ".env" ]; then
    cat <<EOL > .env
DEBUG=False
SECRET_KEY=41&l85x$t8g5!wgvzxw9_v%jbph2msibr3x7jww5%1u8w*3ax

DB_ENGINE=postgresql
DB_HOST=postgres
DB_NAME=db_name
DB_USERNAME=db_user
DB_PASS=db_pass
DB_PORT=5432

CONFIG_EMAIL_ENABLE=False
CONFIG_EMAIL_USE_TLS=True
CONFIG_EMAIL_HOST=smtp.domain.com
CONFIG_EMAIL_HOST_USER=mail@mail.dev.br
CONFIG_DEFAULT_FROM_EMAIL=mail@mail.dev.br
CONFIG_EMAIL_HOST_PASSWORD=password
CONFIG_EMAIL_PORT=587

CONFIG_AUDITOR_MIDDLEWARE_ENABLE = True
DJANGO_CACHE_REDIS_URI=redis://redis:6379/0

RENDER_EXTERNAL_HOSTNAME=https://pdl.denky.dev.br
RENDER_EXTERNAL_FRONTEND=https://pdl.denky.dev.br

CELERY_BROKER_URI=redis://redis:6379/1
CELERY_BACKEND_URI=redis://redis:6379/1
CHANNELS_BACKEND=redis://redis:6379/2

ENCRYPTION_KEY = 'iOg0mMfE54rqvAOZKxhmb-Rq0sgmRC4p1TBGu_JqHac='
DATA_UPLOAD_MAX_MEMORY_SIZE = 31457280

LINEAGE_DB_NAME=l2jmobius
LINEAGE_DB_USER=barao
LINEAGE_DB_PASSWORD=root
LINEAGE_DB_HOST=192.168.100.7
LINEAGE_DB_PORT=3306

CONFIG_MERCADO_PAGO_ACCESS_TOKEN = "APP_USR-0000000000000000-000000-00000000000000000000000000000000-000000000"
CONFIG_MERCADO_PAGO_PUBLIC_KEY = "APP_USR-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
CONFIG_MERCADO_PAGO_CLIENT_ID = "0000000000000000"
CONFIG_MERCADO_PAGO_CLIENT_SECRET = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
CONFIG_MERCADO_PAGO_SIGNATURE = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

LINEAGE_QUERY_MODULE=dreamv3

CONFIG_HCAPTCHA_SITE_KEY=bcf40348-fa88-4570-a752-2asdasde0b2bc
CONFIG_HCAPTCHA_SECRET_KEY=ES_dc688fdasdasdadasdas4e918093asddsddsafa3f1b

CONFIG_LANGUAGE_CODE="pt"
CONFIG_TIME_ZONE="America/Recife"
CONFIG_DECIMAL_SEPARATOR=','
CONFIG_USE_THOUSAND_SEPARATOR=True
CONFIG_DATETIME_FORMAT='d/m/Y H:i:s'
CONFIG_DATE_FORMAT='d/m/Y'
CONFIG_TIME_FORMAT='H:i:s'
CONFIG_GMT_OFFSET=-3

PROJECT_TITLE=Lineage 2 PDL
PROJECT_AUTHOR=Lineage 2 PDL
PROJECT_DESCRIPTION=O PDL é um painel que nasceu com a missão de oferecer ferramentas poderosas para administradores de servidores privados de Lineage 2. Inicialmente voltado à análise de riscos e estabilidade dos servidores, o projeto evoluiu e se consolidou como uma solução completa para prospecção, gerenciamento e operação de servidores — tudo em código aberto.
PROJECT_KEYWORDS=lineage l2 painel servidor
PROJECT_URL=https://pdl.denky.dev.br
PROJECT_LOGO_URL=/static/assets/img/logo_painel.png
PROJECT_FAVICON_ICO=/static/assets/img/ico.jpg
PROJECT_FAVICON_MANIFEST=/static/assets/img/favicon/site.webmanifest
PROJECT_THEME_COLOR=#ffffff

PROJECT_DISCORD_URL='https://discord.gg/seu-link-aqui'
PROJECT_YOUTUBE_URL='https://www.youtube.com/@seu-canal'
PROJECT_FACEBOOK_URL='https://www.facebook.com/sua-pagina'
PROJECT_INSTAGRAM_URL='https://www.instagram.com/seu-perfil'

CONFIG_STRIPE_WEBHOOK_SECRET='whsec_5dzjceF7LgeYzasdasdasdZpSuPq'
CONFIG_STRIPE_SECRET_KEY='sk_test_51RK0cORmyaPSbmPDEMjN0DaasdasdadadasdafgagdhhfasdfsfnbgRrtdKRwHRakfrQub9SQ5jQEUNvTfrcFxbw00gsqFR09W'

CONFIG_MERCADO_PAGO_ACTIVATE_PAYMENTS=True
CONFIG_STRIPE_ACTIVATE_PAYMENTS=True

RUNNING_IN_DOCKER=True
SLOGAN=True

EOL
  fi
  touch "$INSTALL_DIR/env_created"
fi

if [ ! -f "$INSTALL_DIR/htpasswd_created" ]; then
  echo
  echo "🔐 Configurando autenticação básica (.htpasswd)..."
  read -p "👤 Digite o login para o admin: " ADMIN_USER
  read -s -p "🔒 Digite a senha para o admin: " ADMIN_PASS
  echo
  mkdir -p nginx
  HASHED_PASS=$(python3 - <<EOF
from passlib.hash import bcrypt
print(bcrypt.using(rounds=10).hash("$ADMIN_PASS"))
EOF
)
  echo "$ADMIN_USER:$HASHED_PASS" > nginx/.htpasswd
  echo "✅ Arquivo nginx/.htpasswd criado."
  touch "$INSTALL_DIR/htpasswd_created"
fi

if [ ! -f "$INSTALL_DIR/fernet_key_generated" ]; then
  FERNET_KEY=$(python3 - <<EOF
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
EOF
)
  sed -i "/^ENCRYPTION_KEY=/c\ENCRYPTION_KEY='$FERNET_KEY'" .env
  echo "✅ ENCRYPTION_KEY atualizado no .env."
  touch "$INSTALL_DIR/fernet_key_generated"
fi

if [ ! -f "$INSTALL_DIR/build_executed" ]; then
  echo
  echo "🔨 Copiando e preparando build.sh..."
  cp setup/build.sh .
  chmod +x build.sh

  echo
  echo "🚀 Executando build.sh..."
  ./build.sh || { echo "❌ Falha ao executar build.sh"; exit 1; }

  touch "$INSTALL_DIR/build_executed"
fi

if [ ! -f "$INSTALL_DIR/superuser_created" ]; then
  echo
  echo "👤 Criando usuário administrador no Django..."
  read -p "Username: " DJANGO_SUPERUSER_USERNAME
  read -p "Email: " DJANGO_SUPERUSER_EMAIL
  read -s -p "Password: " DJANGO_SUPERUSER_PASSWORD
  echo
  read -s -p "Confirme a senha: " DJANGO_SUPERUSER_PASSWORD_CONFIRM
  echo

  if [ "$DJANGO_SUPERUSER_PASSWORD" != "$DJANGO_SUPERUSER_PASSWORD_CONFIRM" ]; then
    echo "❌ As senhas não conferem. Abortando."
    exit 1
  fi

  docker compose exec site python3 manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists():
    User.objects.create_superuser(
        username='$DJANGO_SUPERUSER_USERNAME',
        email='$DJANGO_SUPERUSER_EMAIL',
        password='$DJANGO_SUPERUSER_PASSWORD'
    )
    print('✅ Superuser \"$DJANGO_SUPERUSER_USERNAME\" criado com sucesso.')
else:
    print('ℹ️ O usuário \"$DJANGO_SUPERUSER_USERNAME\" já existe.')
"
  touch "$INSTALL_DIR/superuser_created"
fi

popd > /dev/null

touch "$INSTALL_DIR/.install_done"

echo
echo "🎉 Instalação concluída com sucesso!"
echo "Acesse: http://localhost:80"
echo "Para gerenciar o projeto, use:"
echo " - docker compose up -d         # Para iniciar"
echo " - docker compose down          # Para parar"
echo
