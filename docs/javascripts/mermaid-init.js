window.addEventListener("load", () => {
  if (typeof mermaid !== "undefined") {
    mermaid.initialize({
      startOnLoad: true,
      theme: "default",
      securityLevel: "loose",
      flowchart: {
        htmlLabels: true,
        curve: "basis",
      },
    });
  }
});
