import argparse
import json
import os

from PasswordProtectedHttpServer import PasswordProtectedHttpServer

parser = argparse.ArgumentParser()
parser.add_argument("command", help="The command to run", choices=["run", "newconfig"])
args = parser.parse_args()

expected = [
    "host",
    "port",
    "root",
    "login-filepath",
    "index-filepath-from-root",
    "password",
    "token-expiration-in-minutes",
    "secret-key",
]

if args.command == "newconfig":
    if os.path.exists("config.json"):
        print("config.json already exists")
        exit(1)
    with open("config.json", "w") as f:
        f.write(
            "{\n\t" + ",\n\t".join(["\"" + e + "\": " for e in expected]) + "\n}"
        )
        
    print("Created new config.json")
    exit(0)


if not os.path.exists("config.json"):
    print(f"config file not found: {'config.json'}")
    exit(1)
with open("config.json", "r") as f:
    config: dict = json.load(f)

for key in expected:
    if key not in config.keys():
        print(f"Missing '{key}' in config.json")
        exit(1)

PasswordProtectedHttpServer.init(config)
PasswordProtectedHttpServer.run()
