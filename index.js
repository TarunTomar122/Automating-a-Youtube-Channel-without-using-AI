import puppeteer from 'puppeteer'
import { spawn } from 'child_process'

function startBot(data, videoUrl, videoLength) {

  const pythonProcess = spawn('python', ['./scripts/main.py', videoLength, videoUrl, data]);

  pythonProcess.stdout.on('data', (data) => {
    console.log(`Python script output: ${data}`);
  });

  pythonProcess.stderr.on('data', (data) => {
    console.error(`Python script error: ${data}`);
  });

  pythonProcess.on('close', (code) => {
    console.log(`Python script exited with code ${code}`);
  });

}

async function extractHTMLFromYouTubeVideo(videoURL) {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  await page.goto(videoURL);

  setTimeout(async function () {

    await page.waitForSelector('.ytp-heat-map-svg');
    await page.waitForSelector('.ytp-progress-bar');

    const videoLength = await page.evaluate(() => {
      const progressBar = document.querySelector('.ytp-progress-bar');
      return progressBar.getAttribute('aria-valuemax');
    });

    const heatMapContainer = await page.$('.ytp-heat-map-svg');
    if (heatMapContainer) {

      const heatMapHTML = await page.evaluate(el => el.innerHTML, heatMapContainer);

      function extractDAttributeValue(data) {
        let dAttributeValue;
        let dAttributeStartIndex = data.indexOf("class=");
        // console.log(dAttributeStartIndex)

        if (dAttributeStartIndex !== -1) {
          let dAttributeEndIndex = data.indexOf("fill", dAttributeStartIndex);
          if (dAttributeEndIndex === -1) {
            dAttributeEndIndex = data.length;
          }
          dAttributeValue = data.substring(dAttributeStartIndex + 41, dAttributeEndIndex - 2);
        }

        return dAttributeValue;
      }

      let data = extractDAttributeValue(heatMapHTML)

      startBot(data, videoURL, videoLength)


    } else {
      console.log('No heat map container found on this page.');
    }

    await browser.close();

  }, 3000);


}

(async () => {
  const videoURL = 'https://www.youtube.com/watch?v=kg7AZ3SR62c';
  await extractHTMLFromYouTubeVideo(videoURL);
})();
