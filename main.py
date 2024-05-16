# main.py


import dicts
from chat import Chat


chatbot_assistant = Chat(dicts.topics, dicts.question_check, dicts.answer_check, dicts.functions_dict)


def chat():
    print("Вітаю! Чим я можу Вам допомогти?")

    chatbot_assistant.converse()


if __name__ == "__main__":
    chat()
