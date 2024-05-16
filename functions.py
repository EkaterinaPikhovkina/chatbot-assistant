# functions.py
# Functions that a chatbot can perform


import datetime
import mysql.connector
import pymorphy3
from config import DB_CONFIG
import spacy
from toDisplacy import f_displacy
from spacy.tokens import Span
from spacy.language import Language


nlp = spacy.load("uk_core_news_sm")
morph = pymorphy3.MorphAnalyzer(lang='uk')


db_connection = mysql.connector.connect(**DB_CONFIG)
cursor = db_connection.cursor()


def lemmatize_sentense(sentence):
    """
    Lemmatizes a given sentence in Ukrainian, returning the sentence in its base form.
    """
    sentence = sentence.lower()
    tokens = [token.text for token in nlp(sentence) if
              not (token.is_punct or token.is_space or len(token) == 1)]
    sentence = ' '.join([element for element in tokens])

    res_list = []
    for word in sentence.split():
        parsed_word = morph.parse(word)[0]
        res_list.append(parsed_word.normal_form)

    return " ".join(res_list)


def create_doc(text):
    """
    Creates a spaCy document from the lemmatized text.
    """
    lemmatized_sentense = lemmatize_sentense(text)
    return nlp(lemmatized_sentense)


def get_product_info():
    """
    Retrieves and displays product information from the database based on user input.
    """
    try:
        column_names = ["name", "description", "price", "quantity_available"]
        entities_dict = {column_name: [] for column_name in column_names}

        for column_name in column_names:
            cursor.execute(f"SELECT {column_name} FROM products")
            rows = cursor.fetchall()
            entities_dict[column_name] = [row[0] for row in rows]

        my_ents = {}
        for k in entities_dict.keys():
            value = entities_dict[k]
            for v in value:
                if isinstance(v, str):
                    my_ents[lemmatize_sentense(v)] = lemmatize_sentense(k)
                else:
                    my_ents[v] = k

        @Language.component('my_ents_component')
        def to_ents(doc_element):
            spans = []
            for token in doc_element:
                try:
                    for key in my_ents.keys():
                        if isinstance(key, str) and token.lemma_ in key:
                            span = Span(doc_element, token.i, token.i + 1, my_ents[key])
                            if not any(span.start < ent.end and span.end > ent.start for ent in spans):
                                spans.append(span)
                except KeyError:
                    continue
            doc_element.ents = spans
            return doc_element

        if 'my_ents' in nlp.pipe_names:
            nlp.remove_pipe('my_ents')

        nlp.add_pipe("my_ents_component", name="my_ents", last=True)

        print("Що Ви хочете дізнатися?")
        user_input = input(">")
        doc = create_doc(user_input)

        f_displacy(doc, 'ent', 'ent_vis')
        f_displacy(doc, 'dep', 'dep_vis')
        print(nlp.pipe_names)

        products_info = []

        for ent in doc.ents:

            entity_label = ent.label_

            entity_text = ent.text

            cursor.execute(f"SELECT * FROM Products WHERE {entity_label} LIKE %s",
                           ('%' + entity_text + '%',))

            rows = cursor.fetchall()

            for row in rows:
                product_info = f"Назва: {row[1]}\nОпис: {row[2]}\nЦіна: {row[3]}\nКількість: {row[4]}\n"
                if product_info not in products_info:
                    products_info.append(product_info)

        formatted_products_info = "\n".join(products_info)

        if not products_info:
            return "Товари не знайдено."
        else:
            return formatted_products_info

    except mysql.connector.Error as err:
        print("Помилка при виконанні запиту до бази даних:", err)


def purchase_product():
    """
    Handles the process of purchasing products, including order creation and database update.
    """
    try:
        customer_email = input("Введіть вашу електронну адресу: ")
        cursor.execute("SELECT customer_id FROM customers WHERE email = %s",
                       (customer_email,))
        customer_id = cursor.fetchone()

        if customer_id:
            products_to_order = []
            while True:
                product_name = input("Введіть назву продукту (або 'готово', щоб завершити): ")
                if product_name.lower() == 'готово':
                    break

                cursor.execute("SELECT name, price FROM Products WHERE name LIKE %s",
                               ('%' + product_name + '%',))
                product = cursor.fetchone()
                if product:
                    products_to_order.append(product)
                else:
                    print(f"Продукт '{product_name}' не знайдено.")

            if products_to_order:
                total_amount = sum(product[1] for product in products_to_order)

                order_date = datetime.datetime.now().strftime("%Y-%m-%d")
                status_id = 1
                cursor.execute("INSERT INTO orders (customer_id, order_date, status_id, total_amount) "
                               "VALUES (%s, %s, %s, %s)",
                               (customer_id[0], order_date, status_id, total_amount))
                db_connection.commit()

                order_summary = "Замовлення успішно оформлено:\n"
                for product in products_to_order:
                    order_summary += f"{product[0]} - {product[1]}\n"
                order_summary += f"Загальна сума: {total_amount}"

                return order_summary
            else:
                return "Немає продуктів для замовлення."
        else:
            return "Користувача з такою електронною адресою не знайдено."

    except mysql.connector.Error as err:
        print("Помилка при виконанні запиту до бази даних:", err)


def get_order_status():
    """
    Retrieves the status of one or multiple orders based on user input.
    """
    try:
        order_numbers = input("Введіть номер(и) замовлення(ів), розділені пробілом: ")

        orders = order_numbers.split()

        for order_number in orders:
            if not order_number.isdigit():
                return "Введено неправильний формат номера замовлення."

        orders_status = []

        for order_number in orders:
            cursor.execute("SELECT order_id, status_id FROM Orders WHERE order_id = %s",
                           (order_number,))
            order = cursor.fetchone()

            if order:
                cursor.execute("SELECT name FROM orderstatuses WHERE status_id = %s",
                               (order[1],))
                status_name = cursor.fetchone()[0]

                orders_status.append(f"Замовлення №{order[0]} {status_name}.")

        if orders_status:
            return "\n".join(orders_status)
        else:
            return "Замовлення з такими номерами не знайдено."

    except mysql.connector.Error as err:
        print("Помилка при виконанні запиту до бази даних:", err)


def add_new_product():
    """
    Adds a new product to the database based on user input.
    """
    try:
        name = input("Введіть назву продукту: ")
        description = input("Введіть опис продукту: ")
        price = float(input("Введіть ціну продукту: "))
        quantity_available = int(input("Введіть кількість доступних одиниць продукту: "))
        category_id = int(input("Введіть ідентифікатор категорії продукту: "))

        cursor.execute("INSERT INTO Products (name, description, price, quantity_available, category_id) "
                       "VALUES (%s, %s, %s, %s, %s)",
                       (name, description, price, quantity_available, category_id))
        db_connection.commit()

        # Формуємо рядок з внесеними в таблицю даними
        product_info = (f"Назва: {name},\nОпис: {description},\nЦіна: {price},\n"
                        f"Доступна кількість: {quantity_available},\nID категорії: {category_id}")

        return f"Продукт додано до бази даних:\n{product_info}"

    except ValueError:
        return "Помилка: невірний формат введених даних."
    except mysql.connector.Error as err:
        return f"Помилка при виконанні запиту до бази даних: {err}"
