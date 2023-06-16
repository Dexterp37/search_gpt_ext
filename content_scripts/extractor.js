function getPageContent() {
  const pageUrl = document.URL;
  if (pageUrl.startsWith("https://docs.google.com")) {
    // Attempt to extract google doc
    return "Bogus";
  }

  return (new Readability(document.cloneNode(true))).parse();
}

// The last statement is used as the return value of the script.
getPageContent()
