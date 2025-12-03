import py_toon_format
import json

data_small = {"status": "ok", "count": 5}
data_large = {
    "users": [
        {"id": i, "name": f"User{i}", "email": f"user{i}@example.com", "active": True}
        for i in range(10)
    ]
}

print("--- Small Data ---")
json_small = json.dumps(data_small)
toon_small = py_toon_format.encode(data_small)
print(f"JSON ({len(json_small)} chars): {json_small}")
print(f"TOON ({len(toon_small)} chars): {toon_small}")

print("\n--- Large Data ---")
json_large = json.dumps(data_large)
toon_large = py_toon_format.encode(data_large)
print(f"JSON ({len(json_large)} chars): {json_large}")
print(f"TOON ({len(toon_large)} chars): {toon_large}")

print("\n--- Brave Search Data ---")
data_brave = [
    {
        "title": "Python 3.12.0 Release - Python.org",
        "url": "https://www.python.org/downloads/release/python-3120/",
        "description": "Oct 2, 2023 ... Python 3.12.0 is the newest major release of the Python programming language, and it contains many new features and optimizations."
    },
    {
        "title": "Download Python | Python.org",
        "url": "https://www.python.org/downloads/",
        "description": "The official home of the Python Programming Language. ... Download the latest version. Download Python 3.12.0. Download Python 3.12.0."
    },
    {
        "title": "Python 3.12 is out: Here are the new features | InfoWorld",
        "url": "https://www.infoworld.com/article/3707887/python-312-is-out-here-are-the-new-features.html",
        "description": "Oct 2, 2023 ... Python 3.12 includes a number of performance improvements, including better support for the specialized adaptive interpreter."
    }
]
json_brave = json.dumps(data_brave)
toon_brave = py_toon_format.encode(data_brave)
print(f"JSON ({len(json_brave)} chars): {json_brave}")
print(f"TOON ({len(toon_brave)} chars): {toon_brave}")

print("\n--- Nested Data ---")
data_nested = [
    {"id": 1, "details": {"a": 1, "b": 2, "c": [1, 2, 3]}},
    {"id": 2, "details": {"a": 3, "b": 4, "c": [4, 5, 6]}}
]
json_nested = json.dumps(data_nested)
toon_nested = py_toon_format.encode(data_nested)
print(f"JSON ({len(json_nested)} chars): {json_nested}")
print(f"TOON ({len(toon_nested)} chars): {toon_nested}")

print("\n--- Long String Data ---")
data_string = {"content": "line1\nline2\nline3\n" * 50}
json_string = json.dumps(data_string)
toon_string = py_toon_format.encode(data_string)
print(f"JSON ({len(json_string)} chars): {json_string}")
print(f"TOON ({len(toon_string)} chars): {toon_string}")
