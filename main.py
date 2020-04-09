'''
MIT License

Copyright Doctorice (c) 2018

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import random
import facebook
import schedule
from io import BytesIO
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from youtube_api import YoutubeDataApi

YOUTUBE_API_KEY = os.environ['YOUTUBE_API_KEY']
FACEBOOK_API_KEY = os.environ["FACEBOOK_API_KEY"]
VIDEO_ID = 'BxV14h0kFs0'

def Youtube_Scrape(api_key, vid):
	"""
	Scrape metadata details of the video.
	"""
	yt = YoutubeDataApi(api_key)
	TomScott = yt.get_video_metadata(vid)
	return TomScott

def ImgFormatter(file, title, views, numlikes, numdislikes):
	"""
	Generate a image to post to the page.
	"""
	with Image.open('mockup.jpg') as img:
		width, height = img.size
		canvas = ImageDraw.Draw(img)

		roboto_title = ImageFont.truetype('Roboto-Regular.ttf', 28)
		roboto_subtitle = ImageFont.truetype('Roboto-Regular.ttf', 20)
		roboto_likes = ImageFont.truetype('Roboto-Regular.ttf', 11)

		canvas.text((15, height - 90),title,(0, 0, 0),font=roboto_title)
		canvas.text((15, height - 40),str(views) + ' views',(144, 144, 144),font=roboto_subtitle)
		canvas.text((400, height - 32),str(numlikes),(144, 144, 144),font=roboto_likes)
		canvas.text((505, height - 32),str(numdislikes),(144, 144, 144),font=roboto_likes)

		with Image.open(file) as frame:
			basewidth = 801
			wpercent = (basewidth/float(frame.size[0]))
			hsize = int((float(frame.size[1])*float(wpercent)))
			frame = frame.resize((basewidth,hsize), Image.ANTIALIAS)
			img.paste(frame, (14,11))

	bytes = BytesIO()
	img.save(bytes, format='JPEG', optimize=True, quality=85)
	return bytes.getvalue()

#	img.save(file,"JPEG",optimize=True, quality=60)

def facebook_img(fb_token, image, caption, comment):
	"""
	Facebook post image with caption, and comment.
	"""
	graph = facebook.GraphAPI(access_token=fb_token, version="3.1")
	post = graph.put_photo(image=image, message=caption)
	graph.put_object(parent_object=post['post_id'], connection_name='comments',message=comment)

def main():
	"""
	Where the main thing happens all here
	"""
	metadata = Youtube_Scrape(api_key=YOUTUBE_API_KEY, vid=VIDEO_ID)
	file ='frames/' + str(random.randint(0, 639)) + '.jpg'
	title = metadata['video_title']
	views = metadata['video_view_count']
	likes = metadata['video_like_count']
	dislikes = metadata['video_dislike_count']
	img = ImgFormatter(file=file,title=title, views=views,numlikes=likes,numdislikes=dislikes)
	facebook_img(fb_token=FACEBOOK_API_KEY, image=img, caption=f'The video has {str(views)} views.', comment=metadata['video_description'])

#Post the output on cron
main()
schedule.every().day.at("12:05").do(main)

while True:
    schedule.run_pending()
    time.sleep(1)