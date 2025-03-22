function openSummaryWindow(docName, summary) {
    const newWindow = window.open("", `${docName}_Summary`, "width=600,height=400");
    newWindow.document.write("<h3>Summary for " + docName + "</h3>");
    newWindow.document.write("<p>" + summary + "</p>");
}
