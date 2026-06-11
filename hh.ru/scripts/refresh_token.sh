#!/bin/bash
# Обновляет access token через refresh token или client_credentials
# Использование: ./scripts/refresh_token.sh

source ~/.hh_env 2>/dev/null || { echo "Файл ~/.hh_env не найден. Создай его из .hh_env.example"; exit 1; }

if [[ -z "$HH_CLIENT_ID" || -z "$HH_CLIENT_SECRET" ]]; then
  echo "HH_CLIENT_ID или HH_CLIENT_SECRET не заданы в ~/.hh_env"
  exit 1
fi

echo "Запрашиваю новый токен..."

RESPONSE=$(curl -s -X POST "https://hh.ru/oauth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials&client_id=${HH_CLIENT_ID}&client_secret=${HH_CLIENT_SECRET}")

echo "$RESPONSE" | python3 -m json.tool

ACCESS_TOKEN=$(echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('access_token',''))" 2>/dev/null)

if [[ -n "$ACCESS_TOKEN" ]]; then
  # Обновляем токен в файле окружения
  sed -i "s|export HH_TOKEN=.*|export HH_TOKEN=\"${ACCESS_TOKEN}\"|" ~/.hh_env
  echo ""
  echo "Токен обновлён в ~/.hh_env"
  echo "Выполни: source ~/.hh_env"
else
  echo "Не удалось получить токен. Проверь client_id и client_secret."
fi
