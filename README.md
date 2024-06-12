# PasswordProtectedHttpServer
CLI tool for running basic static websites with password protection.

### installation
```bash
git clone https://github.com/marcelm9/PasswordProtectedHttpServer.git
cd chunky
pip install .
```

### commands
```bash
# create new config file
python -m PasswordProtectedHttpServer newconfig

# run server
python -m PasswordProtectedHttpServer run
```

### important info
- When running the server, it will always look for a "config.json" file (unless "--config" is set). This is important, as the paths specified in config.json are relative to the current working directory when launching the server. It is recommended to have the root directory of the server and the config file in the same directory.
- To run the example server, cd into to example_server directory and use the command `poetry run python ../main/PasswordProtectedHttpServer/__main__.py run`.
- If the password is an empty string, the login process will be skipped and the server will act like a regular webserver.
- The "login-filepath" config option is the relative filepath from the current working directory. This is different in "index-filepath-from-root", as this option is the filepath starting from the root directory. The reason for the difference is subtle, as it only lies in the possibility to make the login file inaccessible from the root directory after logging in. For example, if the login file is outside the root directory, when the user tries to open the website he will be prompted to enter the password. After logging in, the user is then unable to access the login file again (without going back in the browser). If the file was located inside the root directory, the user could theoretically directly access the login file via the url. This is avoided by storing the login file outside the root directory.
- In login files no other files can be imported. Any css and js has to be done directly inside the html file. To send the password attempt to the server, send a POST request to the /login endpoint. For more details have a look at the example server.

### disclaimer
I know that the regular Flask server should not be used in production. For static websites however, I do not see any reason to setup anything more complex. Use at your own risk.
