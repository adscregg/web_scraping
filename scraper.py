import bs4
import pandas as pd
import requests

columns = ['Product_Name', 'Price (£)', 'Rating', 'CPU', 'GPU', 'RAM', 'Drive', 'Screen_Size', 'Weight', 'OS']  # columns of the dataframe to store scraped data
products_df = pd.DataFrame(columns=columns)  # create empty dataframe

for page in range(1, 14):  # number of pages to search through
    url = f'https://www.dell.com/en-uk/search/laptop?p={page}&t=Product&c=laptops&f=true'  # url to scrape, with page number in an f string
    response = requests.get(url)  # get the response from the url

    soup = bs4.BeautifulSoup(response.text, 'html.parser')  # parse html
    products = soup.find_all('article')  # search for the article tag, this is the container for each product

    for product in products:  # loop over all products

        name = product.find_all(class_='ps-title')[0].a.text  # product name
        if 'New XPS Tower' in name or 'Dell Premier Sleeve' in name:  # ignore if these names appear as they do not seem to be products on the website
            continue

        rating = product.find(class_='ps-ratings-and-reviews').find(class_='ratings-text')  # the rating of the product
        if rating is not None:
            rating = rating.text  # if the product has a rating, extrat the raw text

        try:
            # search for a class within a class and fin all span tags, the second one is the one containing the price, remove the first character as this is a £ sign
            price = product.find(class_='ps-simplified-price-with-total-savings new-simplified-price-with-total-savings').find(class_='ps-dell-price ps-simplified').find_all('span')[1].text[1:]
            price = float(price.replace(',', ''))  # remove the comma and cast to float
        except:
            price = float(product.find(class_='ps-dell-price ps-simplified').text.strip()[1:].replace(',', ''))  # some products display the proce within a div container so handle for both ways to extract this info

        specs = product.find(class_='iconography-feature-specs')  # the container with specs within

        cpu = specs.find(class_='short-specs ps-dds-font-icon dds_processor').text.strip()  # type of cpu, strip is to remove any new line or extra whitespace characters

        OS = specs.find(class_='short-specs ps-dds-font-icon dds_disc-system').text.strip()

        gpu = specs.find(class_='short-specs ps-dds-font-icon dds_video-card')
        if gpu is not None:
            gpu = gpu.text.strip()  # if the laptop has a gpu, extract the text and remove whitespace and new line characters

        memory = specs.find(class_='short-specs ps-dds-font-icon dds_memory').text.strip()

        drive = specs.find(class_='short-specs ps-dds-font-icon dds_hard-drive')
        if drive is not None:
            drive = drive.text.strip()

        features = product.find(class_='ps-features-icon')
        screen = features.find(class_='ps-dds-font-icon featured-spec dds_display device-laptop').text.strip()
        weight = features.find(class_='ps-dds-font-icon featured-spec dds_weight dimensions-weight')

        if weight is not None:
            weight = weight.text.strip()

        items = pd.DataFrame([[name, price, rating, cpu, gpu, memory, drive, screen, weight, OS]], columns=columns)  # add the information to a single row of a dataframe
        products_df = products_df.append(items, ignore_index=True)  # append the row to the larger dataframe

print(products_df)
