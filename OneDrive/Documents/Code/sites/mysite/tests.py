from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
import datetime
from .models import Question

# Create your tests here.
class QuestionModelTest(TestCase):
    def test_was_published_recently_with_future_question(self):
        """was_published_recently() returns False for questions whose pub_date
        is in the future."""
        time = timezone.now() + datetime.timedelta(days = 30)
        future_question = Question(pub_date = time)
        self.assertIs(future_question.was_published_recently(), False)
        
    def test_was_published_recently_with_old_question(self):
        """was_published_recently() returns False for questions whose pub_date
        is older than 1 day."""
        time = timezone.now() - datetime.timedelta(days = 1, seconds = 1)
        old_question = Question(pub_date = time)
        self.assertIs(old_question.was_published_recently(), False)
        
    def test_was_published_recently_with_recent_question(self):
        """was_published_recently returns True for questions whose pub_date
        was within a day."""
        time = timezone.now() - datetime.timedelta(hours = 23, minutes = 59,\
                           seconds = 59)
        recent_question = Question(pub_date = time)
        self.assertIs(recent_question.was_published_recently(), True)

def create_question(question_text, days):
    """
    Creates a question object with the given 'question_text' and the published
    date, with a given offset of x Days; positive for future dates and negative
    for past dates.
    """
    time = timezone.now() + datetime.timedelta(days = days)
    return Question.objects.create(question_text = question_text, pub_date = time)

class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """Displays appropriate text if no questions are present."""
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No polls are available.')
        self.assertQuerysetEqual(response.context['latest_question_list'],[])
        
    def test_past_question(self):
        """Questions with past publication dates are viewable on the page."""
        create_question(question_text = 'Past Question', days = -30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'],['<Question: Past Question>'])
    
    def test_future_question(self):
        """Questions with future publication dates are not displayed on the page."""
        create_question(question_text = 'Future Question', days = 30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'],[])
        
    def test_future_questions_and_past_questions(self):
        """Tests that, when both past and future questions present, that only 
        the past questions are displayed."""
        create_question(question_text = 'Past Question', days = -30)
        create_question(question_text = 'Future Question', days = 30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: Past Question>'])
    
    def test_two_past_questions(self):
        """Tests that the page displays all past questions"""
        create_question(question_text = 'Past Question 1', days = -30)
        create_question(question_text = 'Past Question 2', days = -5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'],\
                                 ['<Question: Past Question 2>',\
                                  '<Question: Past Question 1>'])
    
class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """The detail view of a question with a pub_date in the future
        returns a 404 Not Found."""
        future_question = create_question(question_text = "Future Question.",\
                                          days = 5)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        
    def test_past_question(self):
        """The detail view of a question with a pub_date in the past display's
        the question_text."""
        past_question = create_question(question_text = 'Past Question',\
                                        days = -5)
        url = reverse('polls:detail', args =(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)
        
class QuestionResultsViewTests(TestCase):
    def test_future_question(self):
        """The results view of a question with a future pub_date should return
        a 404 Not Found error."""
        future_question = create_question(question_text = "Future Question.",\
                                          days = 5)
        url = reverse('polls:results', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        
    def test_past_question(self):
        """The results view of a question with a past pub_date should return
        the results page."""
        past_question = create_question(question_text = "Past Question.",\
                                          days = -5)
        url = reverse('polls:results', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)