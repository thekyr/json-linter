import json

def json_linter(file_path):
    """
    Checks if the JSON file is valid.

    Args:
       file_path (str): Path to JSON file

    Return:
       str: Validation result
    """

    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
#        return "JSON is valid"
        print("JSON is valid. The content is:")
        print(json.dumps(data, indent=4))  # Pretty-print the JSON content
        return "Validation successful."
    except json.JSONDecodeError as e:
        return f"JSON in invalid. Error: {e}"
    except FileNotFoundError:
        return "File path is not correct. Please provide a valid path"
    except Exception as e:
        return f"An unexpected error occured: {e}"

if __name__ == "__main__":
    file_path = input("Enter the path to JSON file:")
    result = json_linter(file_path)
    print(result)
