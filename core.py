from PIL import Image, ImageDraw, ImageFont
import requests, tweepy
from StringIO import StringIO

import json, random, sys
import config



def getImages(order, page, tags = '', style = ''):
    pixParams = {
                'key':config.KEY,
                'q': random.choice(tags.replace(" ", "+").split(",")),
                'orientation':'vertical',
                'safesearch': 'true',
                'image_type': style,
                'order': order,
                'per_page': 200,
                'page': page
                }

    imagesList = requests.get(config.PIXABAY, params=pixParams)
    print imagesList.url
    if imagesList.status_code != requests.codes.ok:
        sys.exit("Can't contact Pixabay, stopping. HTTP error {code}\n {text}".format(code=imagesList.status_code, text=imagesList.text))
        return

    json = imagesList.json()
    return json["hits"]

def urlToImage(url):
    response = requests.get(url)
    img = Image.open(StringIO(response.content))
    return img


def writeOnImage(image, text, fontSize):
    base = image.convert('RGBA')

    txt = Image.new('RGBA', base.size, (255,255,255,0))
    fnt = ImageFont.truetype('./Anonymous.ttf', fontSize)
    d = ImageDraw.Draw(txt)
    height = base.height - 100
    #splitHeadline = textwrap.wrap(text, 44)
    #for line in splitHeadline:
    d.text((10,height), text, font=fnt, fill=(255,255,255,255))
    #    height = height + 22

    im = Image.alpha_composite(base, txt)

    return im

def postToTwitter(imgPath, commentTuple):
    auth = tweepy.OAuthHandler(config.TWITTER_CONSUMER_KEY, config.TWITTER_CONSUMER_SECRET)
    auth.set_access_token(config.TWITTER_OAUTH_TOKEN, config.TWITTER_OAUTH_SECRET)

    api = tweepy.API(auth)

    api.update_with_media(filename=imgPath, status="This is {a} and that is {b}. #{a} #{b}".format(a=commentTuple[0], b=commentTuple[1]))



order = random.choice(('popular', 'latest'))
#Grab image list from Pixabay
batch1images = getImages(order, random.choice((2,3)))
#Select the first image at random in the list
imgAData = random.choice(batch1images)
print imgAData["tags"]
print imgAData["type"]
print imgAData["webformatURL"]

print "batch 2"
#Find a 2nd image in the same style (use category and image_type)
batch2images = getImages(order, 1, imgAData["tags"], imgAData["type"])
imgBData = random.choice(batch2images)
print imgBData["tags"]
print imgBData["type"]
print imgBData["webformatURL"]

#Write 'UI' on one image, 'UX' on the other (or some variation, maybe 'Design' vs 'Experience')
if (imgAData['webformatURL'] == imgBData['webformatURL']):
    sys.exit("Got a pair of identical images. Not posting.")

imgA = urlToImage(imgAData['webformatURL'])
imgB = urlToImage(imgBData['webformatURL'])

comment = random.choice ([('UI', 'UX', 100), ('Design', 'Experience', 50)])

print "Building image"
ui = writeOnImage(imgA, comment[0], comment[2])
ux = writeOnImage(imgB, comment[1], comment[2])
#Combine both images as 1 larger one
pair = [(ui, comment[0]), (ux, comment[1])]
random.shuffle(pair)
width, height = pair[0][0].size
final = Image.new('RGB', (width * 2, height))
final.paste(pair[0][0], (0, 0))
final.paste(pair[1][0], (width, 0))
final.save('final.jpg')

print "Tweeting"
#Post to twitter (maybe add a remark in the tweet body)
postToTwitter("./final.jpg", (pair[0][1], pair[1][1]))
print "Published to Twitter"
sys.exit("Done")
