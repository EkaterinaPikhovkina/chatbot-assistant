# Ukrainian Chatbot
The Ukrainian Chatbot is designed to assist customers in interacting with an online store by providing product information, handling purchases, checking order statuses, and adding new products to the database. By leveraging natural language processing, the chatbot understands user queries in Ukrainian, ensuring a seamless and efficient shopping experience.

## Table of Contents
- [Technologies](#technologies)
- [Usage](#usage)
- [Files Description](#files-description)
- [Key Features](#key-features)
- [Example Queries](#example-queries)

## Technologies
- [Python](https://www.python.org/)
- [spaCy](https://spacy.io/)
- [pymorphy3](https://pymorphy2.readthedocs.io/en/latest/)
- [MySQL](https://www.mysql.com/)

## Usage
To use this chatbot, clone the repository, install the necessary dependencies, and run the main.py file. The chatbot will greet you and prompt you to enter your query in Ukrainian.

Clone the repository:
```sh
$ git clone https://github.com/EkaterinaPikhovkina/chatbot-assistant.git
```

Install the required dependencies:
```sh
$ pip install -r requirements.txt
```

Run the chatbot:
```sh
$ python main.py
```

## Files Description
- [***main.py***](./main.py): Entry point for the chatbot.
- [***chat.py***](./chat.py): Contains the Chat class, which handles user interactions and responses.
- [***functions.py***](./functions.py): Defines various functions that the chatbot can perform, such as retrieving product info and processing purchases.
- [***dicts.py***](./dicts.py): Contains dictionaries for topic keywords, confirmation questions, and function mappings.

## Key Features
- **Lemmatization and NLP**: Utilizes spaCy and pymorphy3 for natural language processing and lemmatization of Ukrainian text.
- **Database Interaction**: Connects to a MySQL database to retrieve and manipulate product and order data.
- **Dynamic Response Generation**: Generates responses based on user input, matching queries to predefined topics and functions.

## Example Queries
- *"Які клавіатури та миші є в наявності?"*
- *"Я хочу оформити замовлення."*
- *"Мені потрібно перевірити статус мого замовлення."*
- *"Мені потрібно додати новий товар до бази даних."*

With this chatbot, users can seamlessly interact with an online store, making their shopping experience more efficient and user-friendly.
