from pyppeteer import launch
import asyncio
import requests
import cv2
import os

# Use the top most popular emotes, or fill in the customs ID array
use_top = 20

async def getBitmaps():
    if os.path.isdir('Custom') == True:
        # Remove the old custom files
        files = os.listdir("Custom")
        for item in files:
            os.remove(f"Custom/{item}")
    else:
        os.mkdir("Custom")
    
    if os.path.isdir('allCustomBitmaps') == True:
        # Remove the old bitmap files
        files = os.listdir("allCustomBitmaps")
        for item in files:
            os.remove(f"allCustomBitmaps/{item}")
    else:
        os.mkdir("allCustomBitmaps")
    
    if os.path.isdir('allCustomIDs') == True:
        # Remove the old ID files
        files = os.listdir("allCustomIDs")
        for item in files:
            os.remove(f"allCustomIDs/{item}")
    else:
        os.mkdir("allCustomIDs")

    browser = await launch({'headless': True})
    page = await browser.newPage()

    custom = 0
    ind = 0
    while custom < use_top:
        # Need to reload the page each time
        await page.goto(f'https://emoji.gg/?sort=downloads')
        image = await page.querySelectorAll('.lazy')
        image_url = await page.evaluate('(image_element) => image_element.getAttribute("src")', image[ind])

        if image_url[-4:] == '.png': # Skip the GIFs
            link = image_url
            name = link[29:-4]
            print(link)

            myfile = requests.get(link)
            open(f'Custom/{custom}.png', 'wb').write(myfile.content)

            # Resize the image to 48 x 48 pixels
            before = cv2.imread(f'Custom/{custom}.png')
            after = cv2.resize(before, (48, 48))
            cv2.imwrite(f'Custom/{custom}.png', after)

            # Extract RGB pixel values
            await page.goto('https://www.boxentriq.com/code-breaking/pixel-values-extractor')

            myinput = await page.querySelector("input[type='file']")
            await myinput.uploadFile(f'Custom/{custom}.png')

            await page.select('#mode', '3')
            await page.click('#extractBtn')

            selector = await page.waitForSelector('#results')
            valueSelector = await selector.getProperty("value")
            values = await valueSelector.jsonValue()

            # Write the RGB values to a text file
            with open(f'tempCustom/{custom}.txt', 'w') as f:
                f.write(values)

            # Use my code to convert RGB to RGB565 format with commas
            await page.goto('https://rgb565.taliyahhuang.repl.co/')

            myinput = await page.querySelector("input[type='file']")
            await myinput.uploadFile(f'tempCustom/{custom}.txt')

            selector = await page.waitForSelector('#paragraph')
            valueSelector = await selector.getProperty('textContent')
            values = await valueSelector.jsonValue()

            split = values.split(',')
            lines = '\n'.join(split)

            # Write the RGB bitmap to individual files
            with open(f'allCustomBitmaps/{custom}.txt', 'w') as f:
                f.write(lines)

            # Write the ID codes to individual files
            with open(f'allCustomIDs/{custom}.txt', 'w') as f:
                f.write(name)
            
            custom += 1

        ind += 1

    # Remove the temp custom files
    files = os.listdir("tempCustom")
    for item in files:
        os.remove(f"tempCustom/{item}")

    await browser.close()

asyncio.get_event_loop().run_until_complete(getBitmaps())
