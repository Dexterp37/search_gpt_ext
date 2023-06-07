/*
On startup, connect to the "ping_pong" app.
*/
let port = browser.runtime.connectNative("ping_pong");
port.onMessage.addListener((response) => {
  console.log("Received: " + response);
});

async function syncHistory() {
  // Grab the last 24h of history.
  let history = await browser.history.search({ text: "" });
  // `history` is an array of object with an id, the url, the
  // title, last visit time, the number of visits.
  let tab_for_readermode = await browser.tabs.create({
    active: false,
    url: history[2].url,
    openInReaderMode: true,
  });
  // Hide the tab.
  // await browser.tabs.hide(tab_for_readermode.id);
  // Kill the tab.
  // await browser.tabs.remove(tab_for_readermode.id);

  return history;
}

/*
On a click on the browser action, send the app a message.
*/
browser.browserAction.onClicked.addListener(() => {
  console.log("Sending:  ping");

  syncHistory().then((data) => {
    const msg = {
        type: "sync",
        data: data
    };
    console.debug(`Submitting readermode`, msg)
    port.postMessage("ping");//msg);
  });
});
