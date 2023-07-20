
# EMOKEYS by Taliyah
# Run this code to automatically download several custom discord emoji
# Remember to upload the emoji from the 'Upload' folder into your server!!
# For animated GIF emoji, use Not Quite Nitro to find and match alias names!

from pyppeteer import launch
import asyncio
import requests
import cv2
import os
from PIL import Image

async def getBitmaps():
     # Use the top most popular emotes, or add a emoji.gg link
    num_downloads = 20
    # Ex: 'https://emoji.gg/pack/1320-hello-kitty' <-- Downloads from Hello Kitty emoji pack
    page_link = ''

    if os.path.isdir('Upload') == True:
        # Remove the old upload files
        files = os.listdir("Upload")
        for item in files:
            os.remove(f"Upload/{item}")
    else:
        os.mkdir("Upload")

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

    os.mkdir("tempCustom")

    browser = await launch({'headless': True})
    page = await browser.newPage()

    custom = 0
    ind = 0
    while custom < num_downloads:
        # Check if there's a emoji pack link, else get most popular emojis
        if page_link == '':
            page_link = 'https://emoji.gg/?sort=downloads'

        # Need to reload the page each time
        await page.goto(page_link)
        image = await page.querySelectorAll('.lazy')
        image_url = await page.evaluate('(image_element) => image_element.getAttribute("src")', image[ind])

        name = ''
        if image_url[-4:] == '.gif' or image_url[-4:] == '.png':
            if image_url[-4:] == '.gif':
                link = image_url
                temp_name = link[29:-4]
                letters = []
                for x in range(len(temp_name) - 1, -1, -1):
                    if temp_name[x] != '_' and temp_name[x] != '-':
                        letters.append(temp_name[x])
                    else:
                        break
                letters.reverse()
                name = ''.join(letters)
                print(link)

                myfile = requests.get(link)
                open(f'Upload/{name}.gif', 'wb').write(myfile.content)

                # Split the GIF into frames
                await page.goto('https://ezgif.com/split')

                myinput = await page.querySelector("input[type='file']")
                await myinput.uploadFile(f'Upload/{name}.gif')
                await page.click('.primary')

                await page.waitForSelector('#target')
                await page.click('.primary')

                await page.waitForSelector('.danger')
                
                # Find only img of the gif
                images = await page.querySelectorAll('img')
                frames = []
                for i in range(len(images)):
                    frame_url = await page.evaluate('(image_element) => image_element.getAttribute("src")', images[i])
                    if frame_url[-4:] == '.gif':
                        frames.append(frame_url)
                # Download the frame near the beginning
                link = 'https:' + frames[int(len(frames) * 0.25)]
                print(link)

                myfile = requests.get(link)
                open(f'tempCustom/{custom}.gif', 'wb').write(myfile.content)

                # Convert the GIF frame to png
                gif=f'tempCustom/{custom}.gif'
                img = Image.open(gif)
                img.save(f'Custom/{custom}.png','png', optimize=True, quality=100)

            elif image_url[-4:] == '.png':
                link = image_url
                temp_name = link[29:-4]
                letters = []
                for x in range(len(temp_name) - 1, -1, -1):
                    if temp_name[x] != '_' and temp_name[x] != '-':
                        letters.append(temp_name[x])
                    else:
                        break
                letters.reverse()
                name = ''.join(letters)
                print(link)

                myfile = requests.get(link)
                open(f'Upload/{name}.png', 'wb').write(myfile.content)
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
    os.rmdir("tempCustom")

    await browser.close()

asyncio.get_event_loop().run_until_complete(getBitmaps())
