

# Search GPT WebExtension

To get this working, there's a little setup to do.

## Setup the backend

```bash
python -m venv .venv
pip install -r backend/requirements.txt
```

### Mac OS/Linux

1. Check that the [file permissions](https://en.wikipedia.org/wiki/File_system_permissions) for "ping_pong.py" include the `execute` permission.
2. Edit the "path" property of "ping_pong.json" to point to the location of "ping_pong.py" on your computer.
3. copy "ping_pong.json" to the correct location on your computer. See [App manifest location ](https://developer.mozilla.org/en-US/Add-ons/WebExtensions/Native_manifests#Manifest_location) to find the correct location for your OS.

### Windows

1. Check you have Python installed, and that your system's PATH environment variable includes the path to Python.  See [Using Python on Windows](https://docs.python.org/2/using/windows.html). You'll need to restart the web browser after making this change, or the browser won't pick up the new environment variable.
2. Edit the "path" property of "ping_pong.json" to point to the location of "ping_pong_win.bat" on your computer. Note that you'll need to escape the Windows directory separator, like this: `"path": "C:\\Users\\MDN\\native-messaging\\app\\ping_pong_win.bat"`.
3. Edit "ping_pong_win.bat" to refer to the location of "ping_pong.py" on your computer.
4. Add a registry key containing the path to "ping_pong.json" on your computer. See [App manifest location ](https://developer.mozilla.org/en-US/Add-ons/WebExtensions/Native_manifests#Manifest_location) to find details of the registry key to add.

To assist in troubleshooting on Windows, there is a script called `check_config_win.py`. Running this from the command line should give you an idea of any problems.

## Installing the WebExtension
To run:

1. `npm install` to install the required dependencies.
2. Open Firefox and load the `about:debugging` page. Click
   [Load Temporary Add-on](https://developer.mozilla.org/en-US/Add-ons/WebExtensions/Temporary_Installation_in_Firefox)
   and select the `manifest.json` file within the folder of an example extension.
   Here is a [video](https://www.youtube.com/watch?v=cer9EUKegG4)
   that demonstrates how to do this.
3. Install the
   [web-ext](https://developer.mozilla.org/en-US/Add-ons/WebExtensions/Getting_started_with_web-ext)
   tool. At the command line, open the example extension's folder and type
   `web-ext run`. This launches Firefox and installs the extension automatically.
   This tool provides some additional development features, such as
   [automatic reloading](https://developer.mozilla.org/en-US/Add-ons/WebExtensions/Getting_started_with_web-ext#Automatic_extension_reloading).

## References

* [Original example WebExtension](https://github.com/mdn/webextensions-examples/tree/main/native-messaging)
