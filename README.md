# INTRO 

Recently we started to use [Secret Server](https://delinea.com/lp/secret-server) as a proxy to access many servers in my company.

Unfortunately only MS-Windows launchers are available in our instance, and I am an (old) Linux user.

So I cooked this simple solution to make my life easier.

# INSTALL

You will need Python 3, and the pyexpect module. 

I recommend to use a virtualenv:
```
python3 -m venv venv
source venv/bin/activate
pip install pyexpect
```
# CONFIGURATION

You will need a plain text file with a list of the servers availables for ssh connection.
This list has a line per server, with the Secret Server ID, an IP address and NAME. Only the first field is user for the connection.

I used the script extract-links.py to generate this file from a downloaded copy of the Secret Server page. I mean the page https://YOUR-SECRET-SERVER/app/#/secrets/view/all. Do not use the page icons to download a list of servers, because this list does not include the numeric identifiers.

# USE

Just launch the script, with some optional parameters:
```
python3 ./secret-ssh.py -u YOUR-USERNAME -s YOUR-PROXY-SECRETSERVER -c secrets.csv
```
