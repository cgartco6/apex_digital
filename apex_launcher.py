import os
import subprocess
from dotenv import load_dotenv
sys.path.append('data')
import popia_compliance_rules  # Security module

# Load environment variables
load_dotenv()

AGENTS = {
    "creator": "creator_agent.py",
    "support": "support_agent.py",
    "growth": "growth_agent.py",
    "devsec": "devsec_agent.py"
}

def start_agent(agent_name):
    """Launch AI agent scripts"""
    if agent_name in AGENTS:
        subprocess.Popen(["python", AGENTS[agent_name]])
        print(f"🚀 {agent_name.upper()} AGENT ACTIVATED")
    else:
        print("❌ Invalid agent name")

def monitor_performance():
    """Check resource usage"""
    if os.getenv("REVENUE") > "20000":  # ZAR threshold
        print("⚠️ UPGRADE READY: Paid AI tools can be activated")

# Start all agents
if __name__ == "__main__":
    for agent in AGENTS.keys():
        start_agent(agent)
    print("\n✅ APEX DIGITAL OPERATIONAL")
    print(f"Owner salary: R{os.getenv('OWNER_SALARY', '10000')}/month")
