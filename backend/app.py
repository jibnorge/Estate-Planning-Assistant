import anthropic
import json
import os

from analysis import analyze_estate_gaps

with open('backend/config/api.txt', 'r') as f:
    API_KEY = f.read()
    
with open('backend/config/clients.json') as f:
    data = json.load(f)
    
ACTIVE_CLIENT = data['clients'][1]['client']

findings = analyze_estate_gaps(ACTIVE_CLIENT)

def build_system_prompt(client, findings):
    findings_text = ""
    for f in findings:
        findings_text += f"""
- [{f['severity']}] Rule {f['rule']}: {f['issue']}
  Consequence: {f['consequence']}
  Action: {f['action']}
"""
  
    client_text = json.dumps(client, indent = 2)
 
    system_prompt = f"""
You are an estate planning assistant for Vesta.
You help clients understand what happens to their accounts when they
die and identify gaps in their current setup.

You have access to this client's actual account data and a list of
issues our analysis engine has already found.

YOUR RULES — follow these absolutely, no exceptions:

1. NEVER execute or confirm any account changes. You are read-only.

2. NEVER give legal advice. Always frame sensitive points as
   "you should confirm this with an estate lawyer."

3. HARD STOP RULE — if the client asks you to make any change,
   update any designation, or take any action on their account,
   respond with exactly this structure:
   "This is where I stop. [explain why this decision must be theirs]
   Here is what you need to do yourself: [specific steps]"

4. Explain everything as if the client has no financial background.
   Never use jargon without immediately explaining it in plain English.

5. Be warm and human — this topic is emotionally heavy. The client
   may be thinking about their own death or a recent loss. Lead with
   empathy before facts.

6. Always prioritize CRITICAL findings first in your responses.
   Do not bury the most urgent issue at the bottom.

7. Never make up information. If you are uncertain, say so and
   recommend they speak with a Vesta advisor.
   
8. NEVER mention the names of any person other than the client themselves.
   Always refer to people by their relationship only — "your spouse", 
   "your ex-spouse", "your child", "your partner", "your brother".
   Never say "Robert" or "Tom" or any other person's name.

CURRENT CLIENT PROFILE:
{client_text}

FINDINGS FROM ANALYSIS ENGINE:
{findings_text}

When the client first messages you, briefly acknowledge what you can
see in their situation and ask what they would like to understand first.
Do not dump all findings at once — let the conversation guide the depth.
"""

    return system_prompt
    
def chat(client, findings):
    ai_client = anthropic.Anthropic(api_key = API_KEY)
    
    system_prompt = build_system_prompt(client, findings)
    
    conversation_history = []
    
    print("\n" + "="*60)
    print(f"  Estate Planning Assistant — {client['name']}")
    print("="*60)
    print("  Type your question and press Enter.")
    print("  Type 'quit' to exit.")
    print("="*60 + "\n")
    
    while True:
        
        user_input = input("You: ").strip()
        
        if user_input.lower() in ['quit', 'q', 'exit']:
            print("\nAssistant: Take care. Remember to follow up with")
            print("a Vesta advisor when you are ready.")
            break
            
        if not user_input:
            continue
        
        conversation_history.append({
            "role": "user",
            "content": user_input
        })
       
        response = ai_client.messages.create(
            model = "claude-haiku-4-5",
            max_tokens = 1024,
            system = system_prompt,
            messages = conversation_history
        )
        
        assistant_message = response.content[0].text
        
        conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })
        
        print(f"\nAssistant: {assistant_message}\n")

if __name__ == "__main__":
    chat(ACTIVE_CLIENT, findings)