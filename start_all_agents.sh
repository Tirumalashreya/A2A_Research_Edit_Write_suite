#!/bin/bash
# macOS-compatible script to start all agents and orchestrator using separate Terminal tabs

echo "📁 Creating outputs directory if it doesn't exist..."
mkdir -p outputs

PROJECT_DIR=$(pwd)
VENV_ACTIVATE="source $PROJECT_DIR/venv/bin/activate"

start_agent() {
  AGENT_NAME=$1
  AGENT_MODULE=$2
  echo "🟢 Starting $AGENT_NAME..."
  osascript -e "tell app \"Terminal\" to do script \"cd '$PROJECT_DIR'; $VENV_ACTIVATE && python3 -m $AGENT_MODULE\""
}

start_agent "Research Agent" "Research_Agent.Research"
sleep 1
start_agent "Editor Agent" "Editor_Agent.Editor"
sleep 1
start_agent "Writer Agent" "Writer_Agent.Writer"
sleep 1
start_agent "Orchestrator Agent" "Orchestration_Agent.orchestrator_a2a"
sleep 2

echo -e "\e[34m🚀 Starting Google A2A API Server (FastAPI via uvicorn)...\e[0m"
osascript -e "tell app \"Terminal\" to do script \"cd '$PROJECT_DIR'; $VENV_ACTIVATE && uvicorn app:app --reload --host 0.0.0.0 --port 8000\""

echo "✅ All agents and API server are starting up. Check the new Terminal tabs!"
