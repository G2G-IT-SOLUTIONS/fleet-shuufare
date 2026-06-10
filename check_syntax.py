import traceback
import sys
from jinja2 import Environment, FileSystemLoader

print("Checking Jinja templates...")
env = Environment(loader=FileSystemLoader("app/templates"))
for template_name in env.list_templates():
    if template_name.endswith('.html'):
        try:
            env.get_template(template_name)
        except Exception as e:
            print(f"Error in {template_name}: {e}")
            
print("Checking fast API app initialization...")
try:
    from app.main import app
    print("App imported successfully.")
except Exception as e:
    print("Error importing app:")
    traceback.print_exc()
