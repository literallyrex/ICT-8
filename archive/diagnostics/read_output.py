with open('migration_output.txt', 'r', encoding='utf-16le') as f:
    text = f.read()

with open('migration_output.json', 'w') as f2:
    import json
    json.dump({'text': text}, f2, indent=2)
