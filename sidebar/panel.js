let myWindowId;
const contentBox = document.querySelector("#content");
const promptInput = document.querySelector("#prompt");
const historyView = document.querySelector("#history");

function updateChatHistory(prompt, response) {
  historyView.value += `You: ${prompt}\n\n`;
  let responseText = "No answer";
  if ("result" in response["message"]) {
    responseText = response["message"]["result"];
  }
  historyView.value += `Search GPT: ${responseText}\n\n`;
}

async function queryGPT(promptText) {
  let pageContext;
  try {
    const readableContext = await getActiveTabContent();
    pageContext = readableContext[0].result.textContent;
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