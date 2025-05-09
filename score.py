import parser
import sys

if __name__ == "__main__":
    url = sys.argv[1]

    json_data = parser.generate_json(url)
    print(json_data)