from bs4 import BeautifulSoup
import requests
import string
import numpy as np

url = "https://newyork.craigslist.org/search/sss?"
count = 0
no_of_ads_to_be_fetched = 3
flag = True
while True:
    response = requests.get(url)  # we got to the website
    data = response.text  # we fetched the HTML code / source code of the website
    # cleaned up the code (Parsing HTML of the website, aka making soup)
    soup = BeautifulSoup(data, "html.parser")
    ads = soup.find_all("div", {"class": "result-info"})
    for ad in ads:
        if count >= no_of_ads_to_be_fetched:
            flag = False
            break
        title = ad.find("a", {"class": "result-title"}).text

        price_tag = ad.find("span", {"class": "result-price"})
        if (price_tag):
            price = price_tag.text
        else:
            price = "Not Listed Publicly"

        link = ad.find("a", {"class": "result-title"}).get('href')
        # working on each individual link found and printing the contents of its web page
        # repeating the process that we did for the homepage:
        ad_response = requests.get(link)
        ad_data = ad_response.text
        ad_soup = BeautifulSoup(ad_data, "html.parser")
        if(ad_soup.find("section", {"id": "postingbody"})):
            ad_description = ad_soup.find(
                "section", {"id": "postingbody"}).text
        else:
            ad_description = "Descripton not available."
        # ad_description = os.linesep.join([s for s in ad_description.splitlines() if s]) #just to remove empty lines
        # import os to use the upper line

        # all_info
        all_info = title + "\n" + price + "\n" + ad_description

        # saving the ads in files
        filename = str(count + 1) + ".txt"
        fout = open("ads\\" + filename, "w", encoding='utf-8')
        fout.write(all_info)
        fout.close()
        print("File", count + 1, "created")
        count += 1

    if flag:  # if 10 ads have NOT been fetched
        url_tag = soup.find("a", {"title": "next page"})
        # if all the "next pages" of the site end before we reach target number of ads, then this will handle it.
        if url_tag.get('href'):
            url = "https://newyork.craigslist.org" + url_tag.get('href')
        else:
            break
    else:
        break

# Frequency dictionary
frequencies = dict()
for i in range(0, no_of_ads_to_be_fetched):
    filename = str(i + 1) + ".txt"
    try:
        fin = open("ads\\" + filename, encoding='utf-8')
    except:
        print("Failed to open", filename)

    # read, case-normalize and tokenize:
    # all words from file in lower case but CONTAMINATED w/punctuations
    words = fin.read().lower().split()
    words = str(words).translate(str.maketrans(string.punctuation,
                                               " " * len(string.punctuation)))  # de-contaminated STRING
    words = words.split()  # de-contaminated LIST

    for word in words:  # store words in dictionary
        if word not in frequencies:
            frequencies[word] = 1
        else:
            frequencies[word] += 1
    fin.close()

# assigning unique id to each word
w2n = dict()
n2w = dict()
i = 0
for k, v in frequencies.items():
    w2n[k] = i
    n2w[i] = k

    i += 1

# Creating document's matrix
cols = len(frequencies)
doc_matrix = np.zeros((no_of_ads_to_be_fetched, cols))
# assigning 1 in doc matrix in the cell whose string is present in that particular file
for i in range(0, no_of_ads_to_be_fetched):
    for n in n2w:
        filename = str(i + 1) + ".txt"
        try:
            fin = open("ads\\" + filename, encoding='utf-8')
        except:
            print("Failed to open", filename)

        reader = fin.read().lower()
        if n2w[n] in reader:
            doc_matrix[i, n] = 1
    fin.close()

# BACKEND READY
# -----

# Query handling
while True:
    query = input("\nWhat do you want to buy? ")
    query = query.lower().split()
    query = str(query).translate(str.maketrans(string.punctuation,
                                            " " * len(string.punctuation)))  # de-contaminated STRING
    query = query.split()  # de-contaminated LIST

    # Creating query matrix
    query_matrix = np.zeros((cols))
    # Obtaining id of the queried word from w2n dictionary
    count = 0
    for token in query:
        if token in w2n:
            uid = w2n[token]
            query_matrix[uid] = 1
            count += 1
    if count == 0:
        print("Your search ", query, "did not match any documents.")
    else:
        # Dot Product
        transpose = doc_matrix.T
        dot_prod = query_matrix.dot(transpose)

        # Used in elimination
        descending_scores = np.sort(dot_prod)[::-1]

        # Ranking the pages
        descending_filenos = np.argsort(dot_prod)[::-1][:no_of_ads_to_be_fetched]

        # Eliminating files with 0 matches
        count = 0
        for score in descending_scores:
            if score < 1:
                break
            else:
                count += 1

        # Printing the matched results
        print("Your results were matched in following files:")
        for i in range(0, count):
            filename = str(descending_filenos[i] + 1) + ".txt"
            print(filename)

    again = input("\n**Search again? [y / any key]: ")
    if again.lower() == 'y':
        continue
    else:
        exit()
