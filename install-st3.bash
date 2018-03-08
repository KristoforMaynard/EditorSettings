#!/usr/bin/env bash

here="$(cd -P $(dirname ${0}) && pwd)"
platform="$(uname)"

user_src="${here}/SublimeText3/User"

if [ "${platform}" == "Darwin" ]; then
  user_dest="${HOME}/Library/Application Support/Sublime Text 3/Packages/User"
elif [ "${platform}" == "Linux" ]; then
  user_dest="${HOME}/.config/sublime-text-3/Packages/User"
fi

if [ -d "${user_dest}" ] || [ -f "${user_dest}" ]; then
  echo "Error: '${user_dest}' already exists" 1>&2
  echo "       Remove this directory and rerun this script" 1>&2
  ls -l "${user_dest}"
else
  # symlink User preferences directory
  mkdir -p "$(dirname "${user_dest}")"
  ln -s "${user_src}" "${user_dest}"
fi
