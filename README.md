

# Search GPT WebExtension

To get this working, there's a little setup to do.

## Setup the backend
Requires Python 3.8+.

1. Download the model from [here](https://gpt4all.io/models/ggml-gpt4all-j-v1.3-groovy.bin) (or the orca-mini model from [here](https://huggingface.co/TheBloke/orca_mini_7B-GGML/resolve/main/orca-mini-7b.ggmlv3.q4_0.bin)) and place it in `backend/models`
2. Run the following instructions:

```bash
python -m venv .venv
pip install -r backend/requirements.txt
.venv/bin/activate
cd backend
python main.py
```

You should now have a webserver running on port 8888.

## Installing the WebExtension
To run:

1. `npm install` to install the required dependencies.
2. Open Firefox and load the `about:debugging` page. Click
   [Load Temporary Add-on](https://developer.mozilla.org/en-US/Add-ons/WebExtensions/Temporary_Installation_in_Firefox)
   and select the `manifest.json` file within the folder of an example extension.
   Here is a [video](https://www.youtube.com/watch?v=cer9EUKegG4)
   that demonstrates how to do this.
3. Click on `Inspect` and focus on the `Network` tab.
4. In the Firefox UI, click the WebExtension puzzle icon and then click on `Search GPT History Example`. This will push the last 24 hours of history to the local database in the backend.
5. In the address bar, type `mozgpt <some question>` where `<some question>` is the prompt.
6. Inspect the answer in the `Network` tab.
