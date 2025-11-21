class PresentationAgent:
    def __init__(self):
        pass

    def present(self, insights):
        print("----- Insights Report -----")
        for insight in insights:
            print(f"- {insight}")
        print("---------------------------")

if __name__ == "__main__":
    print("PresentationAgent: Please use this agent with a list of insights from InsightAgent.")
