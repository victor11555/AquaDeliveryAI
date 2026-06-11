#!/bin/bash
# Проверяет, что токен рабочий, и показывает информацию об аккаунте
source ~/.hh_env 2>/dev/null

if [[ -z "$HH_TOKEN" ]]; then
  echo "HH_TOKEN не задан. Создай ~/.hh_env из .hh_env.example"
  exit 1
fi

echo "Проверяю токен..."
curl -s \
  -H "Authorization: Bearer $HH_TOKEN" \
  -H "HH-User-Agent: recruiting-assistant/1.0 (maksimmolcanov845@gmail.com)" \
  "https://api.hh.ru/me" | python3 -m json.tool
