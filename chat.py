# chat.py


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
        """
        Lemmatizes a given sentence in Ukrainian, returning the sentence in its base form.
        """
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
        """
        Creates a spaCy document from the lemmatized text.
        """
        lemmatized_sentense = self.lemmatize_sentense(text)
        return self._nlp(lemmatized_sentense)

    def nlp_comparing(self, user_input, vocabulary):
        """
        Returns the key of the most similar phrase - function.
        """
        max_similarity = -1
        most_similar_key = None
        user_input_doc = self.create_doc(user_input)

        for key, values in vocabulary.items():
            for value in values:
                value_doc = self.create_doc(value)

                similarity = user_input_doc.similarity(value_doc)

                if similarity > max_similarity:
                    max_similarity = similarity
                    most_similar_key = key

        return most_similar_key, max_similarity

    def respond(self, user_input):
        """
        Processes user input to generate an appropriate response based on predefined topics and similarity thresholds.
        """
        threshold = 0.3

        user_input_doc = self.create_doc(user_input)
        user_input_words = [token.text for token in user_input_doc]

        for key, keywords_list in self._topics.items():
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
        """
        Checks the user's response to a specific topic question and generates an appropriate response.
        """
        threshold = 0.3
        chatbot_answer = ''

        question = self._question_check.get(topic, "Вибачте, щось пішло не так.")
        print(question)

        user_response = input(">")

        most_similar_answer, max_similarity = self.nlp_comparing(user_response, self._answer_check)

        if max_similarity < threshold:
            chatbot_answer = 'Вибачте, я Вас не розумію. \nПерефразуйте своє повідомлення, будь ласка.'
        else:
            if most_similar_answer == "yes":
                chatbot_answer = self._functions_dict.get(topic)()
            elif most_similar_answer == "no":
                chatbot_answer = self.respond(user_response)
        return chatbot_answer

    def converse(self, quit_word="стоп"):
        """
        Initiates a conversation with the user, continuously processing input until the quit word is entered.
        """
        user_input = ""
        while user_input != quit_word:
            user_input = quit_word
            try:
                user_input = input(">")
            except EOFError:
                print(user_input)
            if user_input:
                print(self.respond(user_input))
