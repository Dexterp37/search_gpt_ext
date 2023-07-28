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

async function getContentByTabId(tabId) {
  let tabInfo = await browser.tabs.get(tabId);

  const content = await browser.scripting.executeScript({
    target: {
        tabId: tabId,
    },
    files: [
      "/node_modules/@mozilla/readability/Readability.js",
      "/content_scripts/extractor.js"
    ]
  });
  const rawDOM = await browser.scripting.executeScript({
    target: {
        tabId: tabId,
    },
    func: () => {
      return document.documentElement.outerHTML;
    }
  });


  return {
    url: tabInfo.url,
    rawDOM,
    content,
  };
}

async function getActiveTabContent() {
  const tabs = await browser.tabs.query({
    active: true,
    currentWindow: true,
  });

  const tab = tabs[0];
  return await getContentByTabId(tab.id);
}
