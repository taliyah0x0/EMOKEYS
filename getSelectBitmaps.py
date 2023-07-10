# Run this code to download bitmaps from a folder of saved images

from pyppeteer import launch
import asyncio
import requests
import cv2
import os

# Specify emoji (0) or discord emote (1)
emoji_type = 1
# Fill this in with corresponding characters if emojis
emoji_char = [] # Ex: emoji_char = ['😃', '😍'] <-- Remember to have quotes surrounding each!

folder_name = 'images'

async def getBitmaps():
    files = os.listdir(folder_name)
    for item in files:
        if item == '.DS_Store':
            os.remove(f'{folder_name}/{item}')
    files = os.listdir(folder_name)
    num_download = len(files)

    emojis = os.listdir('allEmojiUnicodes')
    for item in emojis:
        if item == '.DS_Store':
            os.remove(f'allEmojiUnicodes/{item}')
    emojis = os.listdir('allEmojiUnicodes')
    num_emojis = len(emojis)

    customs = os.listdir('allCustomIDs')
    for item in customs:
        if item == '.DS_Store':
            os.remove(f'allCustomIDs/{item}')
    customs = os.listdir('allCustomIDs')
    num_customs = len(customs)

    browser = await launch({'headless': True})
    page = await browser.newPage()

    for e in range(num_download):

        # Resize the image to 48 x 48 pixels
        before = cv2.imread(f'{folder_name}/{files[e]}')
        after = cv2.resize(before, (48, 48))
        cv2.imwrite(f'{folder_name}/{files[e]}', after)

        # Extract RGB pixel values
        await page.goto('https://www.boxentriq.com/code-breaking/pixel-values-extractor')

        myinput = await page.querySelector("input[type='file']")
        await myinput.uploadFile(f'{folder_name}/{files[e]}')

        await page.select('#mode', '3')
        await page.click('#extractBtn')

        selector = await page.waitForSelector('#results')
        valueSelector = await selector.getProperty("value")
        values = await valueSelector.jsonValue()

        # Use my code to convert RGB to RGB565 format with commas
        await page.goto('https://rgb565.taliyahhuang.repl.co/')
        myinput = await page.querySelector("input[type='file']")

        if emoji_type == 0:
            # Write the RGB values to a text file
            with open(f'tempEmoji/{num_emojis}.txt', 'w') as f:
                f.write(values)
            await myinput.uploadFile(f'tempEmoji/{num_emojis}.txt')
        else:
             # Write the RGB values to a text file
            with open(f'tempCustom/{num_customs}.txt', 'w') as f:
                f.write(values)
            await myinput.uploadFile(f'tempCustom/{num_customs}.txt')

        selector = await page.waitForSelector('#paragraph')
        valueSelector = await selector.getProperty('textContent')
        values = await valueSelector.jsonValue()

        split = values.split(',')
        lines = '\n'.join(split)
        
        if emoji_type == 0:
            # Write the RGB bitmap to individual files
            with open(f'allEmojiBitmaps/{num_emojis}.txt', 'w') as f:
                f.write(lines)

            # Get the unicode for the emoji
            codepoint = ord(emoji_char[e])
            lead = hex(codepoint)

            # Characters like ♥ and ♠ don't need converstion to surrogate
            # Write the unicodes to individual files
            if len(lead) != 6:
                offset = 0xD800 - (0x10000 >> 10)

                lead = hex(offset + (codepoint >> 10))
                trail = hex(0xDC00 + (codepoint & 0x3FF))

                with open(f"allEmojiUnicodes/{num_emojis}.txt", "w") as f:
                    f.write(str(lead)[2:] + str(trail)[2:])
            else:
                with open(f"allEmojiUnicodes/{num_emojis}.txt", "w") as f:
                    f.write(str(lead)[2:])
            num_emojis += 1
        else:
            '''# Write the RGB bitmap to individual files
            with open(f'allCustomBitmaps/{num_customs}.txt', 'w') as f:
                f.write(lines)'''
            with open(f'allCustomBitmaps/{num_customs}.txt', 'w') as f:
                f.write('const uint16_t ' + files[e][:-4] + '[2304] PROGMEM = {' + values + '};')

            # Write the ID codes to individual files
            with open(f'allCustomIDs/{num_customs}.txt', 'w') as f:
                f.write(files[e][:-4])
            num_customs += 1
    
    # Remove the temp files
    files = os.listdir("tempEmoji")
    for item in files:
        os.remove(f"tempEmoji/{item}")

    files = os.listdir("tempCustom")
    for item in files:
        os.remove(f"tempCustom/{item}")

    await browser.close()

asyncio.get_event_loop().run_until_complete(getBitmaps())
