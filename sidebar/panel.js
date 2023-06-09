let myWindowId;
const contentBox = document.querySelector("#content");
const promptInput = document.querySelector("#prompt");
const historyView = document.querySelector("#history");

function updateChatHistory(prompt, response) {
  historyView.value += `You: ${prompt}\n\n`;
  let responseText = "No answer";
  if ("answer" in response["message"]) {
    responseText = response["message"]["answer"];
  }
  historyView.value += `Search GPT: ${responseText}\n\n`;
  console.debug(`Received response: `, response["message"]);
}

async function queryGPT(promptText) {
  let pageContext = {};
  try {
    const content = await getActiveTabContent();
    pageContext["textContent"] = content.content[0].result.textContent;
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