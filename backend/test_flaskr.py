import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://santarabantoosoo:123@{}/{}".format(
            'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.question_added = {
            "answer": "Tom Cruise",
            "category": 5,
            "difficulty": 4,
            "question": "What actor did author Anne Rice first denounce, then praise in the role of her beloved Lestat?"
        }

        self.wrong_question = {
            "answer": [1, 23, 4]
        }

        self.search_question = {
            "searchTerm": 'the'
        }

        self.search_wrong = {
            "searchTerm": [1, 2, 3]
        }

        self.quiz = {
            "quiz_category": {'id': '2'},
            'previous_questions': [1, 2]
        }

        self.quiz_wrong_data_types = {
            "quiz_category": [1, 2, 3],
            'previous_questions': [1, 2]
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_all_categories(self):
        """Test  all categories"""
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertLessEqual(len(data['categories']), 6)

    def test_category_beyond_available_page(self):

        res = self.client().get('/categories?specific_id=900')
        # print('-----res---')
        # print(res)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not found')

    def test_all_questions(self):

        # test all questions
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertGreaterEqual(data['total_questions'], 1)
        self.assertGreaterEqual(len(data['categories']), 1)
        self.assertTrue(data['current_category'])

    def test_getting_question_beyond_page(self):
        "testing a page beyond total number of pages"
        res = self.client().get('/questions?page=999')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['message'], 'Not found')

    def test_delete_question(self):
        res = self.client().delete('/questions/11')
        data = json.loads(res.data)

        ques_id = [item['id'] for item in data['questions']]
        # print(ques_id)

        self.assertEqual(res.status_code,200)
        self.assertNotIn(11, ques_id)

    def test_delete_unavailable_question(self):

        # delete a questions that is not available
        res = self.client().delete('/questions/999')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['message'], "Not found")
        self.assertFalse(data['success'])

    def test_post_question_to_game(self):
        # post question to game

        num_questions = Question.query.count()

        res = self.client().post('/questions', json=self.question_added)
        data = json.loads(res.data)

        new_num_questions = Question.query.count()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(new_num_questions, num_questions + 1)

    def test_post_question_without_the_question_field(self):
        res = self.client().post('/questions', json=self.wrong_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'request unable to be processed')

    # def test_search(self):
    #     res = self.client().post('/search')
    #     data = json.loads(res.data)

    #     self.assertEqual(res.status_code, 200)

    # def test_search_for_nothing(self):
    #     res = self.client().post('/search')
    #     data = json.loads(res.data)

    #     self.assertEqual(res.status_code, 400)
    #     self.assertFalse(data['success'])
    #     self.assertEqual(data['message'], 'bad request')

    # def test_delete_question(self):

    #     num_questions = Question.query.count()

    #     res = self.client().delete('/questions/4')
    #     data = json.loads(res.data)

    #     new_num_questions = Question.query.count()

    #     self.assertEqual(res.status_code, 200)
    #     self.assertEqual(new_num_questions, num_questions - 1)

    def test_delete_missing_question(self):

        res = self.client().delete('/questions/123123')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['message'], "Not found")
        self.assertFalse(data['success'])

    def test_search(self):
        res = self.client().post('/questions', json=self.search_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data)

    def test_search_with_list(self):
        res = self.client().post('/questions', json=self.search_wrong)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'bad request')

    def test_question_by_category(self):
        res = self.client().get('/categories/2/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertGreaterEqual(len(data['questions']), 1)

    def test_question_by_category_beyond(self):
        res = self.client().get('/categories/99/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['message'], "Not found")
        self.assertFalse(data['success'])

    def test_quiz(self):
        res = self.client().post('/quizzes', json=self.quiz)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['question'])

    def test_wrong_quiz(self):
        res = self.client().post('/quizzes', json=self.quiz_wrong_data_types)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'request unable to be processed')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
