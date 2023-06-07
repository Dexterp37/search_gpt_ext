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
