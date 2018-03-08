#!/usr/bin/env bash

here="$(cd -P $(dirname ${0}) && pwd)"
platform="$(uname)"

user_src="${here}/VSCode/User"

if [ "${platform}" == "Darwin" ]; then
  user_dest="${HOME}/Library/Application Support/Code/User"
  ext_dest="${HOME}/.vscode/extensions"
elif [ "${platform}" == "Linux" ]; then
  user_dest="${HOME}/.config/Code/User"
  ext_dest="${HOME}/.vscode/extensions"
fi

if [ -d "${user_dest}" ] || [ -f "${user_dest}" ]; then
  echo "Error: '${user_dest}' already exists" 1>&2
  echo "       Remove this directory and rerun this script" 1>&2
  ls -l "${user_dest}"
else
  # symlink User preferences directory
  mkdir -p "$(dirname "${user_dest}")"
  ln -s "${user_src}" "${user_dest}"

  # install personal extensions
  mkdir -p "${ext_dest}"

  # symlink xkod color scheme into extensions directory
  # for extname in "extA" "extB" "..."; do
  for extname in "xkod"; do
    rm -rf "${ext_dest}/${extname}"
    ln -s "${user_src}/${extname}" "${ext_dest}/${extname}"
  done
fi
