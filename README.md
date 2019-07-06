# okoye
Telegram Channel Autoforwarder

## Windows Installation Notes

 1. Download and install Python version 3.7  from here: https://www.python.org/downloads/windows/
    Check "Add Python 3.7 to PATH" and select "Install Now"
 2. Open Windows PowerShell. Install pipenv:
    1. `pip install --user pipenv`
 3. Download and extract okoye code from this site (okoye-master)
 4. Open the `channels.yml` file. fill in:
    1. target with the channel you want to forward to
    2. source with the list of the channels you want to forward from
    3. reject (this is optional) with the channel to forward rejected messages
 5. Find 'Environment Variables' in the Control Panel. Add 'C:\Users\[username]\AppData\Roaming\Python\Python37\Scripts'
    to `Path`. Note you need to replace [username] with your windows username
 6. Close Powershell and open it again (to reload the path)
 7. Go to the okoye-master folder in the Powershell with `cd .\okoye-master`
 8. Install dependencies with `pipenv install`
 9. Go to pipenv shell with `pipenv shell`
10. Setup environment variables:
    ```
    $env:TG_SESSION="okoye"
    $env:TG_API_HASH="190e67efb52a447b796f25a710921b4f"
    $env:TG_API_ID=267159
    $env:TG_PHONE="+628xxxx"
    ```
    Replace the `TG_PHONE` number with your phone number
11. Execute the program:
    ```
    python main.py
    ```
12. Terminate the application with `Ctrl-C`.

## Ubuntu Linux Installation Notes

These should work on Ubuntu Linux 16.04 or later (tested on 19.04).

 1. Make sure `pip` is installed
    ```
    $ sudo apt install python-pip
    ```
 2. Install pipenv:
    ```
    $ pip install --user pipenv
    ```
 3. Download and extract okoye code from this site (okoye-master)
 4. Open the `channels.yml` file. fill in with the telegram channel name / username / invite link:
    1. target with the channel you want to forward to
    2. source with the list of the channels you want to forward from
    3. reject (this is optional) with the channel to forward rejected messages
 5. Go to the okoye-master folder with
    ```
    $ cd ./okoye-master
    ```
 6. Install dependencies with
    ```
    $ pipenv install
    ```
 7. Go to pipenv shell with
    ```
    $ pipenv shell
    ```
 8. Setup environment variables:
    ```
    $ export TG_SESSION="okoye"
    $ export TG_API_HASH="190e67efb52a447b796f25a710921b4f"
    $ export TG_API_ID=267159
    $ export TG_PHONE="+628xxxx"
    ```
    Replace the `TG_PHONE` number with your phone number
 9. Execute the program:
    ```
    $ python main.py
    ```
10. Terminate the application with `Ctrl-C`. If you run this on a remote server
    you'll need to execute this using `byobu` terminal so you can keep the
    application running while you're disconnected.
