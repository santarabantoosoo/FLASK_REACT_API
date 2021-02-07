import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category
# from icecream import ic

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, total):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in total]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
    cors = CORS(app, resources={r"/questions/*": {"origins": "*"}})
    # cors = CORS(app)
    '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Headers',
            'Content-Type,Authorization,true')
        response.headers.add(
            'Access-Control-Allow-Methods',
            'GET,PUT,POST,DELETE,OPTIONS')
        return response

    '''
  @TODO:
  Create an endpoint to handle GET requests
  for all available categories.
  '''
    @app.route('/categories')
    def get_categories():

        cat_id = request.args.get('specific_id', None, type=int)

        if cat_id is not None:

            if cat_id > len(Category.query.all()):
                abort(404)
            else:
                categories = [
                    category.format() for category in Category.query.filter_by(
                        id=cat_id).order_by(
                        Category.id).all()]

        categories = [category.format()
                      for category in Category.query.order_by(Category.id).all()]

        all_cats = {cat.id: cat.type for cat in Category.query.all()}

        return jsonify({
            'categories': all_cats,
            'success': True
        })

    '''
  @TODO:
  Create an endpoint to handle GET requests for questions,
  including pagination (every 10 questions).
  This endpoint should return a list of questions,
  number of total questions, current category, categories.

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions.
  '''

    @app.route('/questions')
    def get_questions():

        total = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, total)
        current_category = request.args.get('category', 'Science', type=str)
        categories = [category.format()
                      for category in Category.query.order_by(Category.id).all()]


        all_cats = {cat.id: cat.type for cat in Category.query.all()}
              
        # cat_type = []

        # for category in categories:
        #     cat_type.append(category['type'])

        if len(current_questions) == 0:
            abort(404)

        return jsonify({
            'questions': current_questions,
            'total_questions': Question.query.count(),
            'categories': all_cats,
            'current_category': current_category
        })

    '''
  @TODO:
  Create an endpoint to DELETE question using a question ID.

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page.
  '''
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        # question = Question.query.filter(Book.id == book_id).one_or_none()
        question = Question.query.get(question_id)

        if question is None:
            abort(404)

        question.delete()
        total = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, total)
        current_category = request.args.get('category', 'Science', type=str)
        categories = [category.format()
                      for category in Category.query.order_by(Category.id).all()]
        # cat_type = []

        # for category in categories:
        #     cat_type.append(category['type'])
        all_cats = {cat.id: cat.type for cat in Category.query.all()}

        return jsonify({
            'questions': current_questions,
            'total_questions': Question.query.count(),
            'categories': all_cats,
            'current_category': current_category
        })

    '''
  @TODO:
  Create an endpoint to POST a new question,
  which will require the question and answer text,
  category, and difficulty score.


  TEST: When you submit a question on the "Add" tab,
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.
  '''
    @app.route('/questions', methods=['POST'])
    def add_question():
        body = request.get_json()

        if body.get('searchTerm'):
            try:

                search_term = body.get('searchTerm')

                if not search_term:
                    abort(400)

                term = '%' + search_term + '%'

                total = Question.query.filter(
                    Question.question.ilike(term)).all()

                current_questions = paginate_questions(request, total)

                if len(current_questions) == 0:
                    return('No questions with this search term')

                return jsonify({
                    'questions': current_questions,
                    'total_questions': Question.query.count(),
                })

            except Exception:
                abort(400)
        else:
            new_question = body.get('question', None)
            new_answer = body.get('answer', None)
            new_difficulty = body.get('difficulty', None)
            new_category = body.get('category', None)

            if not new_question:
                abort(422)
            try:
                new_question = Question(
                    question=new_question,
                    answer=new_answer,
                    difficulty=new_difficulty,
                    category=new_category)
                print(new_question)

                new_question.insert()

                return jsonify({
                    'success': True
                })

            except Exception:
                abort(400)

    '''
  @TODO:
  Create a POST endpoint to get questions based on a search term.
  It should return any questions for whom the search term
  is a substring of the question.

  TEST: Search by any phrase. The questions list will update to include
  only question that include that string within their question.
  Try using the word "title" to start.
  '''
    # @app.route('/search', methods=['POST'])
    # def search_questions():

    #     try:
    #         body = request.get_json()

    #         search_term = body.get('searchTerm')

    #         if not search_term:
    #             abort(400)

    #         term = '%' + search_term + '%'

    #         total = Question.query.filter(Question.question.ilike(term)).all()

    #         current_questions = paginate_questions(request, total)

    #         if len(current_questions) == 0:
    #             return('No questions with this search term')

    #         return jsonify({
    #             'questions': current_questions,
    #             'total_questions': Question.query.count(),
    #         })

    #     except BaseException:
    #         abort(400)

    '''
  @TODO:
  Create a GET endpoint to get questions based on category.

  TEST: In the "List" tab / main screen, clicking on one of the
  categories in the left column will cause only questions of that
  category to be shown.
  '''
    @app.route('/categories/<id>/questions')
    def get_questions_by_cat(id):
        try:
            # id = str(int(id) + 1)
            # print(id)
            total = Question.query.filter_by(category=id).all()
            current_questions = paginate_questions(request, total)
            print(total)

            if len(current_questions) == 0:
                abort(404)
            # id = int(id - 1)
            # id = str(int)
        except BaseException:
            abort(404)

        return jsonify({
            'questions': current_questions,
            'total_questions': Question.query.count(),
            'current_category': id
        })

    '''
  @TODO:
  Create a POST endpoint to get questions to play the quiz.
  This endpoint should take category and previous question parameters
  and return a random questions within the given category,
  if provided, and that is not one of the previous questions.

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not.
  '''
    @app.route('/quizzes', methods=['POST'])
    def play_quiz():

        try:
            body = request.get_json()
            print(body)
            catg = body.get('quiz_category')
            catg = catg.get('id')

            previousQuestions = body.get('previous_questions')

            print('cat', catg)
            print('prv', previousQuestions)            
            ques_in_cat = Question.query.filter_by(category=catg).all()
            
            available_ques = [
                av_ques for av_ques in ques_in_cat if Question.id not in previousQuestions]
            print('----')

            ques = random.choice(available_ques)

            ques_id = ques.id

            previousQuestions.append(ques_id)

            ques_cat = Category.query.get(ques.category)

            quizCategory = ques_cat.format()

            currentQuestion = ques.format()

            print('qs_form', currentQuestion)
            print('qs_cat', quizCategory)
            print(previousQuestions)
        except Exception as e:
            print(e)
            abort(422)

        return jsonify({
            'question': currentQuestion,
            'previousQuestions': previousQuestions,
            # 'quizCategory': quizCategory,
            # 'categories': 0
        })

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'message': 'Not found',
            'status_code': 404,
            'success': False
        }), 404

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'message': 'bad request',
            'status_code': 400,
            'success': False
        }), 400

    @app.errorhandler(422)
    def not_processed(error):
        return jsonify({
            'message': 'request unable to be processed',
            'status_code': 422,
            'success': False
        }), 422

    return app

    '''
  @TODO:
  Create error handlers for all expected errors
  including 404 and 422.
  '''
