import os
import spacy
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression


class NLUCore:
    """
    Core NLU for intent predictions.
    """

    def __init__(self, db_name='data.csv'):
        self.root_path = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
        self.db_path = f'{self.root_path}/data/{db_name}'
        self.classifier = None
        self.classes = None
        self.label_encoder = None
        self.spacy_nlp = spacy.load('en_core_web_lg')
        self.extracted_entities = None

        X, y = self.__pre_process_data()
        self.__initialize_classifier(X, y)

    def __pre_process_data(self):
        """
        Obtains X and y data from a data frame. Encodes label and data as numpy values.
        :return:
        """
        df = pd.read_csv(self.db_path)

        X_as_text = df['text']
        y_as_text = df['intent']

        # Tokenize the words for TRAIN
        n_queries = len(X_as_text)
        dim_embedding = self.spacy_nlp.vocab.vectors_length
        X = np.zeros((n_queries, dim_embedding))

        for idx, sentence in enumerate(X_as_text):
            doc = self.spacy_nlp(str(sentence))
            X[idx, :] = doc.vector

        # Encode labels
        le = LabelEncoder()
        y = le.fit_transform(y_as_text)

        self.classes = le.classes_
        self.label_encoder = le

        return X, y

    def __initialize_classifier(self, X, y):
        """
        Initializes and trains a multi-class logistic classifier to fit any of the intents in the training data.
        :param X: Vector embeddings representing the sentences belonging to a particular class intent.
        For example: "Hi!" belongs to "greeting" intent.
        :param y: Labels encoded for the different class intents.
        :return: Initializes internally the logistic classifier.
        """
        classifier = LogisticRegression(random_state=0).fit(X, y)
        self.classifier = classifier

    def __extract_entities(self, text, prediction):
        """
        Entity extraction for the user utterances, needed to complete the slots details
        :param text: The user utterance in need to be parsed
        :param prediction: Prediction of the utterance type, in case we need to perform extra steps to detect properly
        entities for a particular utterance type
        :return: A list containing all the entities recognized, set to the class proeprties
        """
        doc = self.spacy_nlp(text)
        for ent in doc.ents:
            print(ent, ent.label_)

        self.extracted_entities = doc.ents

    def predict_intent(self, text):
        """
        Prediction made over a particular sentence provided by the user. For instance: 'I`m looking  for a restaurant'
        would predict a 'restaurant_search' intent, so the DM module would know how to react properly.
        :param text: Sentence provided by the user.
        :return: Best class label prediction and a vector with probabilities for all classes.
        """
        word_vector = self.spacy_nlp(text).vector

        enc_prediction = self.classifier.predict(np.array(word_vector).reshape(1, -1))
        probabilities = self.classifier.predict_proba(np.array(word_vector).reshape(1, -1))

        prediction = self.label_encoder.inverse_transform([enc_prediction])
        self.__extract_entities(text, prediction[0])

        return prediction[0], probabilities[0]
