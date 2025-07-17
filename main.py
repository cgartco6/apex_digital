from agents.creator_agent import CreatorAgent
from agents.support_agent import SupportAgent, app as support_app
from agents.growth_agent import GrowthAgent
from agents.devsec_agent import DevSecAgent
import threading
from utils.security_utils import *
from utils.payment_utils import *
from utils.media_utils import *
from utils.agent_utils import *
from utils.system_utils import *
from utils.sa_utils import *

def run_support_agent():
    support_app.run(port=5000)

if __name__ == '__main__':
    # Start support agent in a thread
    t = threading.Thread(target=run_support_agent)
    t.daemon = True
    t.start()

    # Now, we can run other agents
    creator = CreatorAgent()
    text = creator.generate_text("Write a blog about AI in South Africa")
    print(text)

    # Similarly, we can trigger other agents
