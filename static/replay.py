import json
import os

transcript_path = r'C:\Users\customer\.gemini\antigravity\brain\a353175f-4e5f-413c-8b7d-6d2dcc86b173\.system_generated\logs\transcript.jsonl'
output_path = 'app_reconstructed.js'

content = ''

try:
    with open(transcript_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i > 1925: # Stop before line 1937
                break
                
            data = json.loads(line)
            for tc in data.get('tool_calls', []):
                func_name = tc.get('name', '')
                args = tc.get('args', {})
                if isinstance(args, str):
                    try:
                        args = json.loads(args)
                    except:
                        continue
                        
                target = args.get('TargetFile', '')
                if 'app.js' in target:
                    if func_name == 'write_to_file':
                        # Overwrite or create
                        content = args.get('CodeContent', '')
                    elif func_name == 'replace_file_content':
                        start = int(args.get('StartLine', 1)) - 1
                        end = int(args.get('EndLine', len(content.split('\n'))))
                        target_str = args.get('TargetContent', '')
                        replacement_str = args.get('ReplacementContent', '')
                        
                        lines = content.split('\n')
                        
                        # Find the target_str in the specified range
                        # This is a bit tricky, but since it's an exact match:
                        chunk = '\n'.join(lines[start:end])
                        if target_str in chunk:
                            new_chunk = chunk.replace(target_str, replacement_str, 1)
                            lines = lines[:start] + new_chunk.split('\n') + lines[end:]
                            content = '\n'.join(lines)
                        else:
                            print(f"Warning: Target string not found at step {i}")

    with open(output_path, 'w', encoding='utf-8') as out:
        out.write(content)
    print("Reconstruction complete. Output saved to app_reconstructed.js")

except Exception as e:
    print(f"Error: {e}")
