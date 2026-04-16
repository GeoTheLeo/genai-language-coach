from app.core.agent import agent

response = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "Generate 5 advanced phrases in Spanish for a German speaker."
            }
        ]
    }
)

# Extract only final response (last AI message)
final_message = response["messages"][-1].content

print("\n=== CLEAN OUTPUT ===\n")
print(final_message)