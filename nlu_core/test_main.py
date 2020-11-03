import unittest
from main import Core


class TestCoreMethods(unittest.TestCase):

    def test_get_instance(self):
        instance = Core()
        self.assertTrue(instance is not None)

    def test_predict_greet(self):
        instance = Core()
        prediction, probabilities = instance.predict_intent('Hi there!')

        self.assertTrue(prediction is not None)
        self.assertTrue(probabilities is not None)

        self.assertTrue(prediction == 'greet')
        self.assertEqual(len(probabilities), 3)

    def test_predict_goodbye(self):
        instance = Core()
        prediction, probabilities = instance.predict_intent('see ya')

        self.assertTrue(prediction is not None)
        self.assertTrue(probabilities is not None)

        self.assertTrue(prediction == 'goodbye')

    def test_predict_restaurant_search(self):
        instance = Core()
        prediction, probabilities = instance.predict_intent('Where can I find a french restaurant?')

        self.assertTrue(prediction is not None)
        self.assertTrue(probabilities is not None)

        self.assertTrue(prediction == 'restaurant_search')

if __name__ == '__main__':
    unittest.main()