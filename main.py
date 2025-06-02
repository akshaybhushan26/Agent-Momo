from dotenv import load_dotenv
from openai import OpenAI
import json
import os
import subprocess
import platform

load_dotenv()

client = OpenAI()

# Tool Definitions
def run_system_command(cmd: str):
    try:
        result = os.system(cmd)
        if result == 0:
            return f"✅ Command executed successfully"
        elif "mkdir" in cmd and result == 256:
            return f"ℹ️ Directory already exists (exit code {result}) - continuing..."
        else:
            return f"⚠️ Command executed with exit code {result}"
    except Exception as e:
        return f"❌ Command execution failed: {str(e)}"

def write_file(filename: str, content: str):
    try:
        # Create directory if it doesn't exist
        dir_path = os.path.dirname(filename)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        return f"✅ File '{filename}' written successfully."
    except Exception as e:
        return f"❌ Failed to write file '{filename}': {str(e)}"

def read_file(filename: str):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"❌ Failed to read file '{filename}': {str(e)}"
    
def append_to_file(filename: str, content: str):
    try:
        # Create directory if it doesn't exist
        dir_path = os.path.dirname(filename)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        
        with open(filename, "a", encoding="utf-8") as f:
            f.write(content)
        return f"✅ Appended content to '{filename}' successfully."
    except Exception as e:
        return f"❌ Failed to append to file '{filename}': {str(e)}"

def open_file(filename: str):
    try:
        system_platform = platform.system()
        if system_platform == "Windows":
            os.startfile(filename)
        elif system_platform == "Darwin":  # macOS
            subprocess.call(["open", filename])
        else:  # Linux and others
            subprocess.call(["xdg-open", filename])
        return f"✅ Opened file '{filename}' successfully."
    except Exception as e:
        return f"❌ Failed to open file '{filename}': {str(e)}"

available_tools = {
    "run_system_command": run_system_command,
    "write_file": write_file,
    "read_file": read_file,
    "append_to_file" : append_to_file,
    "open_file": open_file,
}

# Agent MOMO System Prompt:
SYSTEM_PROMPT = f"""
    You are an advanced agentic AI, named Agent Momo, specialized in software development who helps users in building Web-Apps. 
    Your goal is to semi-autonomously assist with end-to-end coding tasks, including code generation, debugging and optimization.
    Also ask users if they want anything specific with the UI designing of their Web-App.
    Also suggest user about the potential upgrades that you can do with the Web-App you built.

    Act as a highly skilled, detail-oriented software engineer. 
    Your responses must be structured, efficient, and production-ready. 
    You can reason through complex problems, break them down into steps, and take action accordingly.
    Do not forget to append the code into the files you created.
    Also, if you've made any updates to the files like updating the code do not forget to append it in the file.
    Refrain from adding any errors in the code, go through the code twice or thrice to check if everything is correct or not.
    If the folder/file already exists then continue to update the files in the folder but if not then create one.
    Provide the guide to run the app as well
      
    You **must** respond in a structured JSON format for each step. Your response will always include a `"step"` field with values like `"plan"`, `"action"`, `"output"`, `"error"`.
    
    You are allowed to:
    - Ask clarifying questions when information is ambiguous.
    - Generate, explain, and refactor code in modern languages and frameworks (e.g., HTML, CSS, JavaScript, TypeScript, React etc.).
    - Simulate or suggest terminal commands, version control operations (Git) & deployment guidelines.

    Rules:
    - Follow industry best practices.
    - Include meaningful comments and documentation.
    - Ensure readability and maintainability.
    - Do not forget to append the code into the files you created.
    - ALWAYS output a separate "action" step using "append_to_file" or "write_file" to add your code into the appropriate file.
    - Never just show code — always include a file action to persist it.

        
    Available Tools:
    1. "run_system_command" — Execute system commands and return the exit code. Note: Non-zero exit codes aren't always errors (e.g., mkdir on existing directory).
    2. "write_file" — Write new content to a file. Requires filename and content parameters. Creates directories automatically.
    3. "append_to_file" — Append content to an existing file. Requires filename and content parameters. Creates directories automatically.
    4. "read_file" — Read and return the contents of a file. Requires filename parameter.
    5. "open_file" — Open a file using the systems default application. Requires filename parameter.
    
    IMPORTANT: When using write_file or append_to_file, you MUST provide both filename and content as separate parameters in your JSON input object like this:
    {{"filename": "path/to/file", "content": "your code here"}}
    
    COMMAND EXECUTION NOTES:
    - Exit code 0 = Success
    - Exit code 256 for mkdir usually means directory already exists - this is OK, continue with your task
    - Other non-zero codes may indicate actual errors
    - Always analyze the context of the command and exit code before treating it as an error
    
    Output JSON Format:
    {{
        "step": "<plan | action | output | open | error>",
        "content": "<description of the step / code / result>",
        "function": "<optional: name of the function/tool>",
        "input": "<optional: input to the function - for multi-param functions, use JSON object>"
    }}
    
    
    An Example breakdown of the schema you should follow:
    1. Planning stage:
        {{
            "step": "plan",
            "content": "We'll create a TODO list app using HTML, CSS, and JS. It will allow users to add, delete, and mark tasks as complete. Do you have any UI preferences (dark/light theme, minimal layout, etc)?"
        }}
        
    2. Tool Action Stage:
        {{
            "step": "action",
            "function": "run_system_command",
            "input": "mkdir todo-app && cd todo-app",
            "content": "Creating project folder."
        }}
        
        For file operations with multiple parameters:
        {{
            "step": "action",
            "function": "write_file",
            "input": {{"filename": "todo-app/index.html", "content": "<!DOCTYPE html>..."}},
            "content": "Creating the main HTML file for the TODO app."
        }}

    3. Final Output Stage:
        {{
            "step": "output",
            "function": "open_file",
            "input": "todo-app/index.html",
            "content": "Here's the completed TODO list app code. I've opened it for you. Let me know if you want enhancements like drag-and-drop or local storage support."
        }}
    
        
    4. Error Handling Stage:
        {{
            "step": "error",
            "content": "Failed to execute the command."
        }}
        
"""

# Message Initialisation
messages = [{ "role": "system", "content": SYSTEM_PROMPT }]

print("🚀 Agent Momo ready. Type 'exit' or 'quit' to stop.")

while True:
    user_input = input("\n> ")
    if user_input.lower() in {"exit", "quit"}:
        print("👋 Exiting Agent Momo. Goodbye!")
        break

    messages.append({ "role": "user", "content": user_input })

    while True:
        try:
            response = client.chat.completions.create(
                model="gpt-4.1",  
                response_format={"type": "json_object"},
                messages=messages
            )
            content = response.choices[0].message.content
            parsed = json.loads(content)
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing failed: {e}")
            break
        except Exception as e:
            print(f"❌ OpenAI API Error: {e}")
            break

        messages.append({ "role": "assistant", "content": content })

        step = parsed.get("step")
        if step == "plan":
            print(f"\n🧠 Planning:\n{parsed.get('content')}")
            if "?" in parsed.get('content', ''):
                break
            else:
                continue

        elif step == "action":
            tool = parsed.get("function")
            tool_input = parsed.get("input")
            
            if tool is None:
                print(f"⚠️ No tool specified in action step. Skipping.")
                continue

            if tool not in available_tools:
                print(f"❌ Unknown tool: {tool}")
                continue
            
            print(f"🛠️ Using tool: {tool}")
            print(f"🔧 Tool input: {tool_input}")
            
            try:
                if isinstance(tool_input, dict):
                    result = available_tools[tool](**tool_input)
                elif isinstance(tool_input, str):
                    result = available_tools[tool](tool_input)
                else:
                    print(f"❌ Invalid input type for tool {tool}: {type(tool_input)}")
                    continue
                    
                print(f"📋 Result: {result}")
                
                # Send result back to model
                messages.append({
                    "role": "user",
                    "content": json.dumps({ "step": "action", "output": result })
                })
                continue
                
            except Exception as e:
                print(f"❌ Tool execution failed: {str(e)}")
                messages.append({
                    "role": "user",
                    "content": json.dumps({ "step": "action", "output": f"Tool execution failed: {str(e)}" })
                })
                continue

        elif step == "output":
            print(f"\n✅ Output:\n{parsed.get('content')}")
            
            if parsed.get("function"):
                tool = parsed.get("function")
                tool_input = parsed.get("input")
                
                if tool in available_tools:
                    try:
                        if isinstance(tool_input, dict):
                            result = available_tools[tool](**tool_input)
                        else:
                            result = available_tools[tool](tool_input)
                        print(f"📋 {result}")
                    except Exception as e:
                        print(f"❌ Failed to execute {tool}: {str(e)}")
            break

        elif step == "error":
            print(f"\n🚨 Error:\n{parsed.get('content')}")
            break

        else:
            print(f"⚠️ Unknown step type: {step}")
            break