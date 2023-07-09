from pyppeteer import launch
import asyncio
import requests
import cv2
import os

number_to_download = 5
customs = []


async def getBitmaps():
    # Remove the old file with all the previous bitmaps generated
    files = os.listdir('allCustomBitmaps')
    for item in files:
        os.remove(f'allCustomBitmaps/{item}')

    browser = await launch({'headless': True})
    page = await browser.newPage()

    custom = 0
    ind = 0
    while custom < number_to_download:
        # Need to reload the page each time
        await page.goto(f'https://emoji.gg/?sort=downloads')
        image = await page.querySelectorAll('.lazy')
        image_url = await page.evaluate('(image_element) => image_element.getAttribute("src")', image[ind])

        if image_url[-4:] == '.png':
            custom += 1

            link = image_url
            name = link[29:-4]
            print(link)

            myfile = requests.get(link)
            open(f'Custom/{name}.png', 'wb').write(myfile.content)

            # Resize the image to 64 x 64 pixels
            before = cv2.imread(f'Custom/{name}.png')
            after = cv2.resize(before, (64, 64))
            cv2.imwrite(f'Custom/{name}.png', after)

            # Extract RGB pixel values
            await page.goto('https://www.boxentriq.com/code-breaking/pixel-values-extractor')

            myinput = await page.querySelector("input[type='file']")
            await myinput.uploadFile(f'Custom/{name}.png')

            await page.select('#mode', '3')
            await page.click('#extractBtn')

            selector = await page.waitForSelector('#results')
            valueSelector = await selector.getProperty("value")
            values = await valueSelector.jsonValue()

            # Write the RGB values to a text file
            with open(f'tempCustom/{name}.txt', 'w') as f:
                f.write(values)

            # Use my code to convert RGB to RGB565 format with commas
            await page.goto('https://rgb565.taliyahhuang.repl.co/')

            myinput = await page.querySelector("input[type='file']")
            await myinput.uploadFile(f'tempCustom/{name}.txt')

            selector = await page.waitForSelector('#paragraph')
            valueSelector = await selector.getProperty('textContent')
            values = await valueSelector.jsonValue()

            split = values.split(',')
            lines = '\n'.join(split)

            with open(f'allCustomBitmaps/{name}.txt', 'a') as f:
                f.write(lines)

            '''
            # Write values to a new document in Arduino format
            # Variables with hyphen don't work in Arduino, so convert to underscore
            split = name.split('-')
            noHyphen = '_'.join(split)
            new_name = 'custom_' + noHyphen

            with open(f'allCustomBitmaps.txt', 'a') as f:
                f.write('static const uint16_t PROGMEM ' +
                        f'{new_name}[4096] = ' + '{' + values + '};\n')
            '''

        ind += 1
    await browser.close()

asyncio.get_event_loop().run_until_complete(getBitmaps())
