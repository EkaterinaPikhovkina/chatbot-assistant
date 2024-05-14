import dicts
from chat import Chat


eliza_chatbot = Chat(dicts.topics, dicts.question_check, dicts.answer_check, dicts.functions_dict)


def chat():
    print("Вітаю! Чим я можу Вам допомогти?")

    eliza_chatbot.converse()


if __name__ == "__main__":
    chat()
