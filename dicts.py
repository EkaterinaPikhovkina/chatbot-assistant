# dicts.py


import functions


# Dictionary mapping topics to related keywords in Ukrainian.
# Used to determine the topic of the user's input based on keyword matching.
topics = {
    "info": (
        "бути",
        "наявність",
        "інформація",
        "детальний",
        "опис",
        "характеристика",
        "рекомендація",
        "параметр",
        "асортимент",
    ),
    "purchase": (
        "купити",
        "оформити",
        "покупка",
        "кошик",
        "придбати",
    ),
    "status": (
        "статус",
        "доставка",
        "прибуття",
        "очікування",
        "відправлення",
    ),
    "add": (
        "база",
        "додати",
        "новий",
        "поповнення",
        "оновлення",
    )
}


# Dictionary mapping topics to confirmation questions in Ukrainian.
# Used to ask the user for confirmation about their intended action.
question_check = {
    "info": "Ви хочете отримати інформацію про наш асортимент?",
    "purchase": "Ви хочете оформити замовлення?",
    "status": "Ви хочете перевірити статус замовлення?",
    "add": "Ви хочете додати товар до бази даних?",
}


# Dictionary mapping affirmative and negative responses to corresponding keywords in Ukrainian.
# Used to interpret the user's yes or no responses to the confirmation questions.
answer_check = {
    "yes": ("так", "правильно", "безумовний", "точний", "абсолютний"),
    "no": ("не", "ні", "неправильно", "відмовитися", "неправильно", "відхилити")
}


# Dictionary mapping topics to their corresponding functions.
# Used to execute the appropriate function based on the user's confirmed topic.
functions_dict = {
    "info": functions.get_product_info,
    "purchase": functions.purchase_product,
    "status": functions.get_order_status,
    "add": functions.add_new_product,
}
