
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

// On a click on the browser action, send the app a message.
browser.browserAction.onClicked.addListener(() => {
  syncHistory().then(data => sendMessage(
    {
      type: "sync",
      data: data
    })
  );
});

async function storeContent(content) {
  let pageContext = {};
  try {
    pageContext["textContent"] = content.content[0].result.textContent;
    pageContext["rawDOM"] = content.rawDOM[0].result;
    pageContext["pageUrl"] = content.url;
  } catch (e) {
    console.error(`Failed to get context from the current page`, e);
  }

  sendMessage({
    type: "store",
    data: {
      context: pageContext
    }
  })
}

// This automatically submits page content to the backend.
browser.tabs.onUpdated.addListener(
  // The listener.
  (tabId, changeInfo, tabInfo) => {
    if (changeInfo.status != "complete") {
      return;
    }

    console.log(`Updated tab: ${tabId}`);
    console.log("Changed attributes: ", changeInfo);
    console.log("New tab Info: ", tabInfo);

    getContentByTabId(tabId)
      .then(r => storeContent(r))
      .catch(e => console.error(`Error while parsing content for tab ${tabId}`, e));
  },
  // The filter: only look for 'complete' status updates.
  {
    properties: ["status"],
  }
);
