from magi.util.agent import DispatchAgent, agentmethod
from magi.util.processAgent import initializeProcessAgent

# The FileCreator agent implementation, derived from DispatchAgent.
class FileCreator(DispatchAgent):
    def __init__(self):
        DispatchAgent.__init__(self)
        self.filename = '/users/arapapor/magi-modules/FileCreator/calc.aal'

    # A single method which creates the file named by self.filename.
    # (The @agentmethod() decorator is not required, but is encouraged.
    #  it does nothing of substance now, but may in the future.)
    @agentmethod()
    def createFile(self, msg):
        # '''Create a file on the host.'''
        
        # open and immediately close the file to create it.
        #open(self.filename, 'w').close()
        #cwd = os.path.dirname(sys.argv[0])
        #copy2(cwd + "/math.aal", cwd + "/calc.aal")
        
        with open("calc.aal", "a+") as wf:
            with open("math.aal", "r") as rf:
                sa = "          a: "
                sb = "          b: "
        
                for line in rf:
                    #ln = line.readln()
                    
                    if line == sa:
                        wf.write(sa + str(random.random() * 100) + "/n") 
                    elif line == sb:
                        wf.write(sb + str(random.random() * 100) + "/n") 
                    else:
                        wf.write(ln)
        
        
                
        #of.close()
    
        

# the getAgent() method must be defined somewhere for all agents.
# The Magi daemon invokes this mehod to get a reference to an
# agent. It uses this reference to run and interact with an agent
# instance.
def getAgent(**kwargs):
    agent = FileCreator()
    agent.setConfiguration(None, **kwargs)
    return agent

# In case the agent is run as a separate process, we need to
# create an instance of the agent, initialize the required
# parameters based on the received arguments, and then call the
# run method defined in DispatchAgent.
if __name__ == "__main__":
    agent = FileCreator()
    initializeProcessAgent(agent, sys.argv)
    agent.run()
