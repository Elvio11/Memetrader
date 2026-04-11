#!/bin/bash
cd /workspaces/hermes-agent
source .venv/bin/activate
export HOME=/home/codespace
export HERMES_HOME=/home/codespace/.hermes
exec hermes gateway run
