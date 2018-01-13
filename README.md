# amazon-cart-tracker
Tracks price changes in Amazon shopping cart and gmails an alert when an item changes price above a specified threshold. Info included in the email alert is the item's Amazon link, current price, price change, and CamelCamelCamel price stats and links if available.

The code scrapes Amazon and CamelCamelCamel pages and can breake at any moment without a notice.

For the most part, the code relies on the stock Python libraries with an exception of BeautifulSoup, and is intended to run as a cron job. All of the configuration is done in the config.json which must be in the same directory as the main python code shopping_cart.py (command line options to follow).

Optionally, account info (amazon and gmail login and password) in the config file can provided as encrypted values that are decrypted using a key stored in an environment variable. Encryption can be performed by running code.py.

Downloaded price info is stored in a file 'data.json' (can be configured in config.json). There is also a 'writeoutfiles' flag to tell the script to save downloaded Amazon web pages (useful for debugging).

It is possible Gmail requires a checkbox somewhere on the account config page to allow SMTP. Can't quite remember.

TODO:

The code was cobbled together and mostly serves the purpose as intended. Can use some cleaning, command line customization etc.

Credits:

The project started after trying https://github.com/Sorlas/Amazon-Price-Check and realizing it does something different. Some of the code in the cart tracker could be inspired by that project.