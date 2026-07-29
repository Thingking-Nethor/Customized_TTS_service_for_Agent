#!/bin/bash
cd "/d/GPT-SoVITS/GPT-SoVITS-v2pro-20250604-nvidia50" || exit
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "/d/GPT-SoVITS/GPT-SoVITS-v2pro-20250604-nvidia50" || exit
export PATH="$SCRIPT_DIR/runtime:$PATH"
"$SCRIPT_DIR/runtime/python.exe" -I api_v2.py