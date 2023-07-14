let myWindowId;
const contentBox = document.querySelector("#content");
const promptInput = document.querySelector("#prompt");
const historyView = document.querySelector("#history");

function updateChatHistory(prompt, response) {
  let userLineElement = document.createElement("p");
  userLineElement.textContent = `${prompt}`;
  userLineElement.className = "history-user-entry";
  historyView.appendChild(userLineElement);

  let responseText = "No answer";
  if ("answer" in response["message"]) {
    responseText = response["message"]["answer"];
  }

  let sources = "";
  if (("source_documents" in response["message"])
      && (response["message"]["source_documents"].length > 0)) {
    const hrefTags = response["message"]["source_documents"]
      .map(doc => doc["metadata"]["url"])
      .map(url => `<li><a href="${url}">${url.slice(0, 32)}...</a></li>`);
    sources = `<br>Sources:<br><ul>${hrefTags.join("")}</ul>`;
  }

  let gptLineElement = document.createElement("p");
  gptLineElement.innerHTML = `${responseText}${sources}`;
  gptLineElement.className = "history-gpt-entry";
  historyView.appendChild(gptLineElement);
  gptLineElement.scrollIntoView();

  console.debug(`Received response: `, response);
}

async function queryGPT(promptText) {
  let pageContext = {};
  try {
    const content = await getActiveTabContent();
    pageContext["textContent"] = content.content[0].result.textContent;
    pageContext["rawDOM"] = content.rawDOM[0].result;
    pageContext["pageUrl"] = content.url;
  } catch (e) {
    console.error(`Failed to get context from the current page`, e);
  }

  sendMessage({
    type: "prompt",
    data: {
      prompt: promptText,
      context: pageContext
    }
  }).then((r) => updateChatHistory(promptText, r));
}

function onCheckSubmit(e) {
  var key = e.keyCode;

  // If the user has pressed enter
  if (key === 13) {
    const promptText = promptInput.value;
    queryGPT(promptText);
    promptInput.value = "";
    e.preventDefault();
    return false;
  }
}

promptInput.addEventListener("keydown", (e) => onCheckSubmit(e))