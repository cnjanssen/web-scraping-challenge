from splinter import Browser
from bs4 import BeautifulSoup as bs
import pandas as pd
import time


def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {"executable_path": "/usr/local/bin/chromedriver"}
    return Browser("chrome", **executable_path, headless=False)

def scrape():
    news = scrape_news()
    image = get_featured_img()
    weather = get_weather()
    facts = get_facts()
    hemisphere = get_hemi()
    mars_dict = {
            "news": news ,
            "featured_img" : image,
            "weather" : weather,
            "facts" : facts,
            "hemisphere": hemisphere,
        }
    return mars_dict

#scrape the latest news, returning a list with the title, then the article body
def scrape_news():
    #create variable, "output" which we will return at the end
    output = []
    #visit the Mars and get the latest news. title and paragraph body
    browser = init_browser()

    # visit site
    url = "https://mars.nasa.gov/news"
    browser.visit(url)

    time.sleep(1)

    # Scrape page into Soup
    html = browser.html
    soup = bs(html, "html.parser")

    # Get the latest news title and paragraph text
    new_title = {}
    title = soup.findAll("div", {"class": "content_title"})
    first_paragraph = soup.findAll("div", {"class": "article_teaser_body"})

    
    #create variables for first article headline and its text teaser paragraph
    news_title = title[0].text
    news_p = first_paragraph[0].text

    # Quite the browser after scraping
    browser.quit()
    
    output.append(news_title)
    output.append(news_p)
    
    return output

#return full-size featured image url from NASA's JPL
def get_featured_img():
    #visit JPL mars space image site and get the featured image info 
    #then go to the image library and get the full length jpeg 
    browser = init_browser()
    url_jpl = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    base_url = 'https://www.jpl.nasa.gov'
    browser.visit(url_jpl)
    time.sleep(1)

    # Scrape page into Soup
    html = browser.html
    soup = bs(html, "html.parser")

    #get browser data-link tag
    box = soup.find_all('div', {'class':'carousel_items'})
    #find a attribute
    link = box[0].find('a')
    #find data-link within a
    idl = link['data-link']

    #create url to image
    full_link = str(base_url + idl)

    #visit url of full image metadata and description
    browser.visit(full_link)

    # Scrape page into Soup
    html = browser.html
    soup = bs(html, "html.parser")

    #find all links to the images and return the jpeg link since the class download_tiff appears 
    #twice and references both tiff and jpeg images
    a = soup.find_all('div', {'class':'download_tiff' })
    featured_image_url = a[1].find('a')['href']

    browser.quit()
    return featured_image_url

# get mars weather as a string
def get_weather(): 
    #visit twitter page to get weather
    url_twitter = 'https://twitter.com/marswxreport?lang=en'
    browser = init_browser()
    browser.visit(url_twitter)
    time.sleep(1)

    # Scrape page into Soup
    html = browser.html
    soup = bs(html, "html.parser")

    #get tweet text and save into variable
    tweet = soup.find('p', {'class' : 'TweetTextSize TweetTextSize--normal js-tweet-text tweet-text'})
    text = tweet.contents[0]
    #clean string up 
    mars_weather = text.replace('\n', ' ')

    browser.quit()
    return mars_weather

#return html string
def get_facts():
    #visit page for mars facts and use Pandas
    url = 'https://space-facts.com/mars/'
    browser = init_browser()
    browser.visit(url)

    # get html from browser and read it into pandas using the read_html command
    html = browser.html
    df_list = pd.read_html(html, attrs = {'id': 'tablepress-p-mars-no-2'})
    df = df_list[0]
    df.columns = ['Property', 'Value']
    string = df.to_html()

    browser.quit()
    return string

#return a list of dictionaries for mars hemispheres and their images
def get_hemi():    
    #visit hemisphere image page and collect links as a list of dictionaries
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser = init_browser()
    browser.visit(url)

    # Scrape page into Soup
    html = browser.html
    soup = bs(html, "html.parser")

    #create list of hemisphere titles
    hemi_t = []

    #get list of all links and have browser click on each sequentially
    images = soup.find_all('div', {'class' : 'description'})

    urls = []
    url = images[0].find('a')['href']
    base_url = 'https://astrogeology.usgs.gov'

    #generate complete url list
    for i in images:
        url = i.find('a')['href']
        title = i.find('h3').text
        title_strip = title[:-9]
        hemi_t.append(title_strip)
        full_url = str(base_url+url)
        urls.append(full_url)

    img_links = []

    #iterate through url list, visiting each url and appending it to another list

    for l in urls:
        browser.visit(l)
        html = browser.html
        soup = bs(html, "html.parser")
        images = soup.find_all('div', {'class' : 'downloads'})

        links = images[0].find_all('a')

        tif = links[1]['href']
        img_links.append(tif)
    list_dict = []

    for t, u in zip(hemi_t, img_links):
        hemi_dict = {
            "title": t ,
            "img_url" : u,
        }
        list_dict.append(hemi_dict)
    browser.quit()
    return list_dict


