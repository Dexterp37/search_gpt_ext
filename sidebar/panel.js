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

function onCheckSubmit(e) {
  var key = e.keyCode;

  // If the user has pressed enter
  if (key === 13) {
    const promptText = promptInput.value;
    sendMessage({
      type: "prompt",
      data: promptText
    }).then((r) => updateChatHistory(promptText, r));
    promptInput.value = "";

    e.preventDefault();
    return false;
  }
}


promptInput.addEventListener("keydown", (e) => onCheckSubmit(e))