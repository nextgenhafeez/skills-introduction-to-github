const path = require("path");
const puppeteer = require("../temp_puppeteer/node_modules/puppeteer");

async function main() {
  const htmlPath = path.resolve(__dirname, "blacklayers-ai-plan-presentation.html");
  const outputPath = path.resolve(
    __dirname,
    "BlackLayersAI-Marketing-Agent-Presentation.pdf"
  );

  const browser = await puppeteer.launch({
    headless: "new",
    executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    args: ["--no-sandbox", "--disable-setuid-sandbox"],
  });

  try {
    const page = await browser.newPage();
    await page.goto(`file://${htmlPath}`, { waitUntil: "networkidle0" });
    await page.pdf({
      path: outputPath,
      printBackground: true,
      width: "13.333in",
      height: "7.5in",
      margin: {
        top: "0in",
        right: "0in",
        bottom: "0in",
        left: "0in",
      },
      preferCSSPageSize: true,
    });
    console.log(outputPath);
  } finally {
    await browser.close();
  }
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
