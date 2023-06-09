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
