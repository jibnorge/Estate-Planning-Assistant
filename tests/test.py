import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.analysis import analyze_estate_gaps
import json

with open('backend/config/clients.json') as f:
    data = json.load(f)

for client in data['clients']:
    print(f"\n{'='*50}")
    print(f"  {client['client']['name']} — {client['_scenario']}")
    print(f"{'='*50}")
    results = analyze_estate_gaps(client['client'])
    for f in results:
        print(f"  [{f['severity']}] {f['rule']} — {f['issue']}")
        
all_results = []

for client_wrapper in data['clients']:
    client  = client_wrapper['client']
    results = analyze_estate_gaps(client)

    all_results.append({
        'name':     client['name'],
        'scenario': client_wrapper['_scenario'],
        'findings': results
    })

with open('docs/findings.json', 'w') as f:
    json.dump(all_results, f, indent = 2)

print("findings.json written successfully")