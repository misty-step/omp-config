#!/bin/sh
set -eu
umask 077

mkdir -p ./config
rm -f ./config/server.yaml ./config/database.yaml

key_dir=./config/keys
if [ ! -s "$key_dir/master.key" ] || [ ! -s "$key_dir/private_ec256.key" ] || [ ! -s "$key_dir/public_ec256.key" ]; then
  temporary_keys="./config/.keys.$$"
  rm -rf "$temporary_keys"
  mkdir "$temporary_keys"
  trap 'rm -rf "$temporary_keys"' EXIT HUP INT TERM
  if ! ./hatchet-admin keyset create-local-keys --key-dir "$temporary_keys" >/dev/null 2>&1; then
    echo "Hatchet key generation failed" >&2
    exit 1
  fi
  chmod 0600 "$temporary_keys"/*
  rm -rf "$key_dir"
  mv "$temporary_keys" "$key_dir"
  trap - EXIT HUP INT TERM
fi

cookie_file=./config/auth-cookie-secret
cookie_valid=false
if [ -s "$cookie_file" ]; then
  IFS= read -r cookie_value <"$cookie_file"
  case "$cookie_value" in
    *" "*) cookie_valid=true ;;
  esac
fi
if [ "$cookie_valid" != true ]; then
  temporary_cookie="./config/.auth-cookie-secret.$$"
  temporary_auth="./config/.auth-cookie-auth.$$"
  temporary_encrypt="./config/.auth-cookie-encrypt.$$"
  trap 'rm -f "$temporary_cookie" "$temporary_auth" "$temporary_encrypt"' EXIT HUP INT TERM
  if ! openssl rand -hex 32 >"$temporary_auth" 2>/dev/null ||
     ! openssl rand -hex 32 >"$temporary_encrypt" 2>/dev/null; then
    echo "Hatchet cookie secret generation failed" >&2
    exit 1
  fi
  IFS= read -r cookie_auth <"$temporary_auth"
  IFS= read -r cookie_encrypt <"$temporary_encrypt"
  printf '%s %s\n' "$cookie_auth" "$cookie_encrypt" >"$temporary_cookie"
  rm -f "$temporary_auth" "$temporary_encrypt"
  chmod 0600 "$temporary_cookie"
  mv "$temporary_cookie" "$cookie_file"
  trap - EXIT HUP INT TERM
fi

export SERVER_ENCRYPTION_MASTER_KEYSET_FILE="$key_dir/master.key"
export SERVER_ENCRYPTION_JWT_PRIVATE_KEYSET_FILE="$key_dir/private_ec256.key"
export SERVER_ENCRYPTION_JWT_PUBLIC_KEYSET_FILE="$key_dir/public_ec256.key"
IFS= read -r SERVER_AUTH_COOKIE_SECRETS <"$cookie_file"
export SERVER_AUTH_COOKIE_SECRETS

./hatchet-migrate

if ./hatchet-admin authdisabled >/dev/null 2>&1; then
  token_file=./config/authdisabled-token
  if [ ! -s "$token_file" ]; then
    temporary_token="./config/.authdisabled-token.$$"
    trap 'rm -f "$temporary_token"' EXIT HUP INT TERM
    if ! ./hatchet-admin token create --config ./config --name authdisabled-default >"$temporary_token" 2>/dev/null; then
      echo "Hatchet worker token generation failed" >&2
      exit 1
    fi
    chmod 0600 "$temporary_token"
    mv "$temporary_token" "$token_file"
    trap - EXIT HUP INT TERM
  fi
  chmod 0600 "$token_file"
fi

exec ./hatchet-lite --config ./config
