import time, sched, bs4, requests, datetime, re, mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="Sea4cool",
    database= "eBayProducts"
)

class sql:
    mycursor = db.cursor()
    #mycursor.execute("CREATE TABLE Static(ID int PRIMARY KEY AUTO_INCREMENT, productName VARCHAR(100), productURL VARCHAR(300), imageURL VARCHAR(300))")
    #mycursor.execute("CREATE TABLE Dynamic(ID int PRIMARY KEY AUTO_INCREMENT, productPrice VARCHAR(50), stock BIT(1) , Timestamp TIMESTAMP)")
    #mycursor.execute("TRUNCATE TABLE dynamic")
    #db.commit()

class product:
    
    def __init__ (self, productName, productURL, imageURL, productID, productPrice, productStatus,timeStamp):
        self.productName = str(productName)
        self.productURL = str(productURL)
        self.imageURL = str(imageURL)
        self.productID = int(productID)
        self.productPrice = str(productPrice)
        self.productStatus = productStatus
        self.timeStamp = timeStamp
    def getName(self):
        return self.productName
    def getPURL(self):
        return self.productURL
    def getIURL(self):
        return self.imageURL

    def setTime(self, x):
        self.timeStamp = x
    def getTime(self):
        return self.timeStamp

    def setID(self, x):
        self.productID = x
    def getID(self):
        return self.productID

    def setPrice(self, x):
        self.productPrice = x
    def getPrice(self):
        return self.productPrice
        
    def setStatus(self, x):
        if x == True:
            self.productStatus = 1
        else:
            self.productStatus = 0
    def getStatus(self):
        return self.productStatus

def Scraper(x):
    count = 0
    productList = []
    ts = time.time()
    temp = product
    entryTime = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    page = requests.get(x)
    soup = bs4.BeautifulSoup(page.content, 'html.parser')
    ok = soup.find(class_='b-list__items_nofooter srp-results srp-grid')
    itemListing = ok.findChildren(class_="s-item__wrapper clearfix")
    for i in itemListing:
        #the name of item
        name = i.find(class_="s-item__title").text
      
        #product URL
        pUrl = i.find(class_="s-item__link").get("href")
        
        #product price
        pPrice = i.find(class_= "s-item__price").text
       
        #product Status 
        page2 = requests.get(pUrl)
        soup = bs4.BeautifulSoup(page2.content, 'html.parser')
        status2 = soup.find(class_="page-notice__content")
        status = soup.find(id="status-message")
        if(status == None or status2 == None):
            pStatus = True
        else:
            pStatus = False
        

        #productID information is hidden cant access.
        pID = count
        count+=1
        print(count)
        #soup.find(class_="s-value")
   

        #gets the image url
        iUrl = i.find(class_="s-item__image-img").get("src")
        

        productList.append(temp(name,pUrl,iUrl,pID,pPrice,pStatus, entryTime) )
    for itemListing in productList:
        sql.mycursor.execute("INSERT INTO Static ( productName, productURL, imageURL) VALUES(%s,%s,%s)", (itemListing.getName(),itemListing.getPURL(),itemListing.getIURL()))
        sql.mycursor.execute("INSERT INTO Dynamic ( productPrice, stock, Timestamp) VALUES(%s,%s,%s)", (itemListing.getPrice(),itemListing.getStatus(),itemListing.getTime()))
        db.commit()
    #Dynamic Information: product id, price, stock, timestamp
    while True:
        
        for i in productList:
            page = requests.get(i.getPURL())
            #timestamp
            ts = time.time()
            i.setTime(datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S'))
            soup = bs4.BeautifulSoup(page.content, 'html.parser')
            
            #updated in stock information
            status2 = soup.find(class_="page-notice__content")
            status = soup.find(id="status-message")
            if(status == None or status2 == None):
                i.setStatus(True)
            else:
                i.setStatus(False)
    
            #updated product price   
            if(soup.find(class_="display-price") == None):
                i.setPrice(soup.find(class_="notranslate").text)
            else:
                i.setPrice(soup.find(class_="display-price").text)

            #productID information is hidden cant access.
            #i.setID(soup.find(class_="s-value"))
            sql.mycursor.execute("UPDATE Dynamic SET productPrice = (%s) WHERE ID = (%s)",(i.getPrice(), i.getID())) 
            sql.mycursor.execute("UPDATE Dynamic SET stock = (%s) WHERE ID = (%s)",(i.getStatus(), i.getID()))  
            sql.mycursor.execute("UPDATE Dynamic SET Timestamp = (%s) WHERE ID = (%s)",(i.getTime(), i.getID())) 
            db.commit()
            
        time.sleep(300)