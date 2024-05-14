import datetime
import mysql.connector
import pymorphy3
from config import DB_CONFIG
import spacy
from toDisplacy import fDisplacy
from spacy.tokens import Span
from spacy.language import Language


nlp = spacy.load("uk_core_news_sm")
morph = pymorphy3.MorphAnalyzer(lang='uk')


# З'єднання з базою даних
db_connection = mysql.connector.connect(**DB_CONFIG)
cursor = db_connection.cursor()


def lemmatize_sentense(sentence):
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
    # Перед обробкою тексту виконуємо попередню обробку
    lemmatized_sentense = lemmatize_sentense(text)
    # Повертаємо об'єкт документа
    return nlp(lemmatized_sentense)


def get_product_info():
    try:
        # Визначте назви колонок
        column_names = ["name", "description", "price", "quantity_available"]

        # Створіть порожній словник
        entities_dict = {column_name: [] for column_name in column_names}

        # Додайте дані до словника з кожної колонки
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
        def to_ents(doc):
            spans = []
            for token in doc:
                try:
                    for key in my_ents.keys():
                        if isinstance(key, str) and token.lemma_ in key:
                            span = Span(doc, token.i, token.i + 1, my_ents[key])
                            if not any(span.start < ent.end and span.end > ent.start for ent in spans):
                                spans.append(span)
                except KeyError:
                    continue
            doc.ents = spans
            return doc

        # Перевірка, чи існує компонент 'my_ents' у конвеєрі
        if 'my_ents' in nlp.pipe_names:
            # Видалення компонента 'my_ents' з конвеєра
            nlp.remove_pipe('my_ents')

        # Додавання нового компонента 'my_ents_component'
        nlp.add_pipe("my_ents_component", name="my_ents", last=True)

        print("Що Ви хочете дізнатися?")
        user_input = input(">")
        doc = create_doc(user_input)

        # fDisplacy(doc, 'ent', 'ent_vis')
        # fDisplacy(doc, 'dep', 'dep_vis')
        # print(nlp.pipe_names)

        products_info = []

        # Переглянути всі сутності в документі
        for ent in doc.ents:
            # Отримати мітку сутності
            entity_label = ent.label_

            # Отримати значення тексту сутності
            entity_text = ent.text

            # Виконати SQL-запит з урахуванням мітки сутності та тексту сутності
            cursor.execute(f"SELECT * FROM Products WHERE {entity_label} LIKE %s",
                           ('%' + entity_text + '%',))

            # Отримати результати запиту
            rows = cursor.fetchall()

            # Вивести результати
            for row in rows:
                product_info = f"Назва: {row[1]}\nОпис: {row[2]}\nЦіна: {row[3]}\nКількість: {row[4]}\n"
                if product_info not in products_info:
                    products_info.append(product_info)

        # Форматуємо кожен продукт окремо
        formatted_products_info = "\n".join(products_info)

        if not products_info:
            return "Товари не знайдено."
        else:
            return formatted_products_info

    except mysql.connector.Error as err:
        print("Помилка при виконанні запиту до бази даних:", err)


def purchase_product():
    try:
        # 1. Ідентифікація користувача за електронною адресою
        customer_email = input("Введіть вашу електронну адресу: ")
        cursor.execute("SELECT customer_id FROM customers WHERE email = %s", (customer_email,))
        customer_id = cursor.fetchone()

        if customer_id:
            # 2. Узнати, які продукти хоче купити користувач
            products_to_order = []
            while True:
                product_name = input("Введіть назву продукту (або 'готово', щоб завершити): ")
                if product_name.lower() == 'готово':
                    break

                cursor.execute("SELECT name, price FROM Products WHERE name LIKE %s", ('%' + product_name + '%',))
                product = cursor.fetchone()
                if product:
                    products_to_order.append(product)
                else:
                    print(f"Продукт '{product_name}' не знайдено.")

            # 3. Оформлення замовлення, якщо є продукти для замовлення
            if products_to_order:
                # Підрахунок загальної вартості замовлення
                total_amount = sum(product[1] for product in products_to_order)

                # Оформлення замовлення
                order_date = datetime.datetime.now().strftime("%Y-%m-%d")
                status_id = 1  # Припустимо, що статус "Очікує оплати" має id = 1
                cursor.execute("INSERT INTO orders (customer_id, order_date, status_id, total_amount) VALUES (%s, %s, %s, %s)",
                               (customer_id[0], order_date, status_id, total_amount))
                db_connection.commit()

                # 4. Вивід даних замовлення користувачу
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
    try:
        # Запросить у пользователя номера заказов
        order_numbers = input("Введіть номер(и) замовлення(ів), розділені пробілом: ")

        # Разбиваем строку с номерами заказов на отдельные номера
        orders = order_numbers.split()

        # Перевіряємо, чи введений рядок складається тільки з цифр
        for order_number in orders:
            if not order_number.isdigit():
                return "Введено неправильний формат номера замовлення."

        # Список для хранения информации о статусах заказов
        orders_status = []

        # Перебираем номера заказов
        for order_number in orders:
            # Выполняем запрос к базе данных для каждого номера заказа
            cursor.execute("SELECT order_id, status_id FROM Orders WHERE order_id = %s", (order_number,))
            order = cursor.fetchone()

            # Если найден заказ, добавляем его статус в список
            if order:
                # Получаем название статуса по его идентификатору
                cursor.execute("SELECT name FROM orderstatuses WHERE status_id = %s", (order[1],))
                status_name = cursor.fetchone()[0]

                orders_status.append(f"Замовлення №{order[0]} {status_name}.")

        # Формируем сообщение с информацией о статусах заказов
        if orders_status:
            return "\n".join(orders_status)
        else:
            return "Замовлення з такими номерами не знайдено."

    except mysql.connector.Error as err:
        print("Помилка при виконанні запиту до бази даних:", err)


def add_new_product():
    try:
        # Запит користувача на введення даних для нового продукту
        name = input("Введіть назву продукту: ")
        description = input("Введіть опис продукту: ")
        price = float(input("Введіть ціну продукту: "))
        quantity_available = int(input("Введіть кількість доступних одиниць продукту: "))
        category_id = int(input("Введіть ідентифікатор категорії продукту: "))

        # Вставка нового продукту в базу даних
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
