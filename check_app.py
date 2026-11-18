
from app import app

print("\n===== MEDISENSE AI DIAGNOSTICS =====")

print("APP ROOT:", app.root_path)
print("TEMPLATE FOLDER:", app.template_folder)

for template in ["analysis.html", "ai_intelligence_lab.html", "base.html"]:
    try:
        source, filename, uptodate = app.jinja_loader.get_source(
            app.jinja_env, template
        )
        print(f"\n{template}: FOUND")
        print("PATH:", filename)
    except Exception as error:
        print(f"\n{template}: ERROR")
        print(error)

client = app.test_client()

for route in ["/", "/analysis", "/ai-intelligence-lab"]:
    response = client.get(route)
    print(f"\nROUTE: {route}")
    print("STATUS:", response.status_code)

    if route == "/analysis":
        print("AGE FIELD:", 'name="age"' in response.get_data(as_text=True))
        print(
            "TEST HEADING:",
            "NEW ANALYSIS TEMPLATE TEST" in response.get_data(as_text=True)
        )

    if route == "/":
        print(
            "LAB NAVIGATION:",
            "AI Intelligence Lab" in response.get_data(as_text=True)
        )

print("\n===== DIAGNOSTICS COMPLETE =====")
