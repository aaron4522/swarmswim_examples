#!/bin/bash
pip3 install "ray[rllib]" torch

FOLDER="$(pwd)"

cd "$FOLDER/.." || exit 1

git clone https://github.com/save-xx/SwarmSwIM.git

cd SwarmSwIM || exit 1

pip3 install -e .
