async function sendMessage(msg) {
  const url = `http://localhost:8888/${msg["type"]}`;
  const response = await fetch(url, {
    method: "POST",
    cors: "no-cors",
    cache: "no-cache",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(msg),
  });
  return response.json();
}

async function syncHistory() {
  // Grab the last 24h of history.
  let history = await browser.history.search({ text: "" });
  // `history` is an array of object with an id, the url, the
  // title, last visit time, the number of visits.
  /*let tab_for_readermode = await browser.tabs.create({
    active: false,
    url: history[2].url,
    openInReaderMode: true,
  });*/
  // Hide the tab.
  // await browser.tabs.hide(tab_for_readermode.id);
  // Kill the tab.
  // await browser.tabs.remove(tab_for_readermode.id);

  return history;
}

// https://github.com/mdn/webextensions-examples/blob/f4a611d76b5cb81d759ca037d88fd144b107c827/firefox-code-search/background.js
browser.omnibox.setDefaultSuggestion({
  description: `Search history via LLM
    (e.g. "hello world" | "path:omnibox.js onInputChanged")`
});


// Submit a prompt using the address bar
browser.omnibox.onInputEntered.addListener((text, disposition) => {
  const msg = {
    type: "prompt",
    data: text
  };
  console.debug(`Submitting prompt`, msg);
  sendMessage(msg);
  /*
  let url = text;
  if (!text.startsWith(SOURCE_URL)) {
    // Update the url if the user clicks on the default suggestion.
    url = `${SEARCH_URL}?q=${text}`;
  }
  switch (disposition) {
    case "currentTab":
      browser.tabs.update({url});
      break;
    case "newForegroundTab":
      browser.tabs.create({url});
      break;
    case "newBackgroundTab":
      browser.tabs.create({url, active: false});
      break;
  }*/
});

// On a click on the browser action, send the app a message.
browser.browserAction.onClicked.addListener(() => {
  syncHistory().then(data => sendMessage(
    {
      type: "sync",
      data: data
    })
  );
});
