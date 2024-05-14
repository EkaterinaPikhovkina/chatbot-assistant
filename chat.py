import spacy
import pymorphy3
import warnings


warnings.filterwarnings("ignore")


class Chat:
    def __init__(self, topics, question_check, answer_check, functions_dict):

        self._topics = topics
        self._question_check = question_check
        self._answer_check = answer_check
        self._functions_dict = functions_dict
        self._nlp = spacy.load("uk_core_news_sm")
        self._morph = pymorphy3.MorphAnalyzer(lang='uk')

    def lemmatize_sentense(self, sentence):
        sentence = sentence.lower()
        tokens = [token.text for token in self._nlp(sentence) if
                  not (token.is_punct or token.is_space or len(token) == 1)]
        sentence = ' '.join([element for element in tokens])

        res_list = []
        for word in sentence.split():
            parsed_word = self._morph.parse(word)[0]
            res_list.append(parsed_word.normal_form)

        return " ".join(res_list)

    def create_doc(self, text):
        # Перед обробкою тексту виконуємо попередню обробку
        lemmatized_sentense = self.lemmatize_sentense(text)
        # Повертаємо об'єкт документа
        return self._nlp(lemmatized_sentense)

    def nlp_comparing(self, user_input, vocabulary):
        max_similarity = -1
        most_similar_key = None
        user_input_doc = self.create_doc(user_input)

        # Ітеруємося по кожній темі та її ключовим словам
        for key, values in vocabulary.items():
            for value in values:
                value_doc = self.create_doc(value)

                # Обчислюємо схожість між векторами користувача та теми
                similarity = user_input_doc.similarity(value_doc)

                # Оновлюємо найбільш схожу тему, якщо поточна схожість більша
                if similarity > max_similarity:
                    max_similarity = similarity
                    most_similar_key = key

        return most_similar_key, max_similarity

    def respond(self, user_input):
        threshold = 0.3

        user_input_doc = self.create_doc(user_input)
        user_input_words = [token.text for token in user_input_doc]

        # Проходимося по кожному ключу у словнику тем
        for key, keywords_list in self._topics.items():
            # Перевіряємо, чи є слова з запиту користувача в списку ключових слів теми
            for word in user_input_words:
                if word in keywords_list:
                    topic = key
                    chatbot_answer = self.topic_check(topic)
                    return chatbot_answer

        topic, max_similarity = self.nlp_comparing(user_input, self._topics)

        if max_similarity < threshold:
            chatbot_answer = 'Вибачте, я Вас не розумію. \nПерефразуйте своє повідомлення, будь ласка.'
        else:
            chatbot_answer = self.topic_check(topic)

        return chatbot_answer

    def topic_check(self, topic):
        threshold = 0.3
        chatbot_answer = ''

        # Отримуємо питання для відповіді зі словника question_check
        question = self._question_check.get(topic, "Вибачте, щось пішло не так.")
        print(question)  # Виводимо питання в консоль

        # Очікуємо відповідь користувача
        user_response = input(">")
        # user_response = "так"

        most_similar_answer, max_similarity = self.nlp_comparing(user_response, self._answer_check)

        if max_similarity < threshold:
            chatbot_answer = 'Вибачте, я Вас не розумію. \nПерефразуйте своє повідомлення, будь ласка.'
        else:
            # Якщо відповідь "yes", повертаємо відповідну функцію зі словника functions_dict
            if most_similar_answer == "yes":
                chatbot_answer = self._functions_dict.get(topic)()
            # Якщо відповідь "no", продовжуємо обробку запиту користувача
            elif most_similar_answer == "no":
                chatbot_answer = self.respond(user_response)
        return chatbot_answer

    def converse(self, quit="стоп"):
        user_input = ""
        while user_input != quit:
            user_input = quit
            try:
                user_input = input(">")
                # user_input = "опис"
            except EOFError:
                print(user_input)
            if user_input:
                print(self.respond(user_input))
