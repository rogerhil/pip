#!/usr/bin/env bash
set -x

PWD=$(pwd)

function handle_exit {
  cd $PWD
  echo "FAILED!!!"
}
trap 'handle_exit' EXIT

COMMIT_MSG=$1

git branch | grep pip_9.0.3
if [ $? -ne 0 ]; then
  echo "pip forked repo must be in git branch pip_9.0.3"
  exit 1
fi
python3 -m build
cd pip_for_py26/
cp ../dist/pip-9.0.3-py2.py3-none-any.whl .
md5 -q pip-9.0.3-py2.py3-none-any.whl > pip-9.0.3-py2.py3-none-any.whl.md5
git commit -a -m "${COMMIT_MSG}"
git push origin pip_9.0.3
cd ..
