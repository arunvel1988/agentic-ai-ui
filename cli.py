from agent import agent

while True:

    q = input("\nYou : ")

    if q.lower() == "exit":
        break

    print("\nAgent:")
    print(agent.ask(q))
