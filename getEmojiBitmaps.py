from pyppeteer import launch
import asyncio
import requests
import cv2
import os

# Use top most popular emojis, or fill in the emojis array
use_top = 20
# Ex: emojis = ['🫶', '🥹'] <-- Remember to use quotes surrounding each emoji!
emojis = []


async def getBitmaps():
    if os.path.isdir('Emojis') == True:
        # Remove the old emoji files
        files = os.listdir("Emojis")
        for item in files:
            os.remove(f"Emojis/{item}")
    else:
        os.mkdir("Emojis")

    if os.path.isdir('allEmojiBitmaps') == True:
        # Remove the old bitmap files
        files = os.listdir("allEmojiBitmaps")
        for item in files:
            os.remove(f"allEmojiBitmaps/{item}")
    else:
        os.mkdir("allEmojiBitmaps")

    if os.path.isdir('allEmojiUnicodes') == True:
        # Remove the old unicode files
        files = os.listdir("allEmojiUnicodes")
        for item in files:
            os.remove(f"allEmojiUnicodes/{item}")
    else:
        os.mkdir("allEmojiUnicodes")

    browser = await launch({"headless": True})
    page = await browser.newPage()

    emoji_names = []

    if use_top > 0:
        # Use the top most popular emojis
        await page.goto("https://emojipedia.org/most-popular/")

        selector = await page.querySelectorAll(".emoji")

        for index in range(use_top):
            valueSelector = await selector[index].getProperty("textContent")
            values = await valueSelector.jsonValue()
            emojis.append(values[0])

        selector = await page.querySelectorAll("a")

        length = 0
        index = 0
        while length < 20:
            emoji_name = await page.evaluate('(emoji_element) => emoji_element.getAttribute("href")', selector[index])

            if emoji_name != None:
                if emoji_name[0] == "/" and emoji_name[-1] == "/":
                    emoji_names.append(emoji_name[1:-1])
                    length += 1
            index += 1

    for e in range(len(emojis)):
        # Start by downloading the emoji as an image from Emojipedia
        await page.goto(f"https://emojipedia.org/{emojis[e]}/")

        # If emoji_names array was empty:
        if len(emoji_names) < len(emojis):
            selector = await page.querySelectorAll("h1")
            valueSelector = await selector[0].getProperty("textContent")
            values = await valueSelector.jsonValue()

            split = values[2:].split(" ")
            joined = "-".join(split)

            emoji_names.append(joined.lower())

        # Find the Twitter Twemoji
        link = ""
        image = await page.querySelectorAll("img")
        for item in image:
            image_url = await page.evaluate('(image_element) => image_element.getAttribute("src")', item)
            if image_url[-4:] == ".png":
                if image_url[:50] == "https://em-content.zobj.net/thumbs/120/twitter/351":
                    link = image_url
                    myfile = requests.get(link)
                    open(f"Emojis/{e}.png", "wb").write(myfile.content)
                    break

        # Resize the image to 48 x 48 pixels
        before = cv2.imread(f"Emojis/{e}.png")
        after = cv2.resize(before, (48, 48))
        cv2.imwrite(f"Emojis/{e}.png", after)

        # Extract RGB pixel values
        await page.goto("https://www.boxentriq.com/code-breaking/pixel-values-extractor")

        myinput = await page.querySelector("input[type='file']")
        await myinput.uploadFile(f"Emojis/{e}.png")

        await page.select("#mode", "3")
        await page.click("#extractBtn")

        selector = await page.waitForSelector("#results")
        valueSelector = await selector.getProperty("value")
        values = await valueSelector.jsonValue()

        # Write the RGB values to a text file
        with open(f"tempEmoji/{e}.txt", "w") as f:
            f.write(values)

        # Use my code to convert RGB to RGB565 format with commas
        await page.goto("https://rgb565.taliyahhuang.repl.co/")

        myinput = await page.querySelector("input[type='file']")
        await myinput.uploadFile(f"tempEmoji/{e}.txt")

        selector = await page.waitForSelector("#paragraph")
        valueSelector = await selector.getProperty("textContent")
        values = await valueSelector.jsonValue()

        # Write values to individual documents
        split = values.split(",")
        lines = "\n".join(split)

        # Write the RGB bitmap to individual files
        with open(f"allEmojiBitmaps/{e}.txt", "w") as f:
            f.write(lines)

        # Get the unicode for the emoji
        codepoint = ord(emojis[e])
        lead = hex(codepoint)

        # Characters like ♥ and ♠ don't need converstion to surrogate
        # Write the unicodes to individual files
        if len(lead) != 6:
            offset = 0xD800 - (0x10000 >> 10)

            lead = hex(offset + (codepoint >> 10))
            trail = hex(0xDC00 + (codepoint & 0x3FF))

            with open(f"allEmojiUnicodes/{e}.txt", "w") as f:
                f.write(str(lead)[2:] + str(trail)[2:])
        else:
            with open(f"allEmojiUnicodes/{e}.txt", "w") as f:
                f.write(str(lead)[2:])

    # Remove the temp emoji files
    files = os.listdir("tempEmoji")
    for item in files:
        os.remove(f"tempEmoji/{item}")

    await browser.close()


asyncio.get_event_loop().run_until_complete(getBitmaps())
