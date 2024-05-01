import unittest
from app import app

class TestApp(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.app = app.test_client()
        self.test_user = {'emailName': 'test@test.com', 'pw': 'test'}

    def test_index_route(self):
        # Test GET request to / route
        index_response = self.app.get('/')
        self.assertEqual(index_response.status_code, 200)
        self.assertIn(b'Welcome to Balanced Budgets', index_response.data)

    def test_get_dashboard_page_success(self):
        # Test successful GET request to /dashboard/ route
        # Login test user
        login_response = self.app.post('/login/', data=self.test_user, follow_redirects=True)
        self.assertEqual(login_response.status_code, 200)

        # Test GET request to /dashboard/ route
        dashboard_response = self.app.get('/dashboard/')
        self.assertEqual(dashboard_response.status_code, 200)
        self.assertIn(b'Budgeting Dashboard', dashboard_response.data)

    def test_get_dashboard_page_failure_not_logged_in(self):
        # Test GET request to /dashboard/ route without logging in
        dashboard_response = self.app.get('/dashboard/', follow_redirects=True)
        self.assertEqual(dashboard_response.status_code, 200)

        # User is redirected to index
        self.assertIn(b'Welcome to Balanced Budgets', dashboard_response.data)

    def test_get_login_page_success(self):
        # Test successful GET request to /login/ route
        login_response = self.app.get('/login/')
        self.assertEqual(login_response.status_code, 200)
        self.assertIn(b'Sign in to start saving!', login_response.data)

    def test_get_login_page_failure_already_logged_in(self):
        # Test GET request to /login/ while already logged in
        # Login test user
        login_response = self.app.post('/login/', data=self.test_user, follow_redirects=True)
        self.assertEqual(login_response.status_code, 200)

        # Test GET request to /login/
        second_login_response = self.app.get('/login/', follow_redirects=True)
        self.assertEqual(second_login_response.status_code, 200)

        # User is redirected back to dashboard
        self.assertIn(b'Looks like you&#39;re already logged in!', second_login_response.data)

    def test_post_login_success(self):
        # Test POST request to /login/ with correct credentials
        login_response = self.app.post('/login/', data=self.test_user, follow_redirects=True)
        self.assertEqual(login_response.status_code, 200)
        self.assertIn(b'You&#39;ve been logged in!', login_response.data)
        self.assertIn(b'Budgeting Dashboard', login_response.data)

    def test_post_login_failure_incorrect_everything(self):
        # Test POST request to /login/ with incorrect credentials
        login_response = self.app.post('/login/', data={'emailName': 'invalid@example.com', 'pw': 'invalid_password'}, follow_redirects=True)
        self.assertEqual(login_response.status_code, 200)
        self.assertIn(b'Incorrect Username or Password', login_response.data)
        self.assertIn(b'Sign in to start saving!', login_response.data)

    def test_post_login_failure_incorrect_password(self):
        # Test POST request to /login/ with correct email but incorrect password
        login_response = self.app.post('/login/', data={'emailName': 'test@test.com', 'pw': 'invalid_password'}, follow_redirects=True)
        self.assertEqual(login_response.status_code, 200)
        self.assertIn(b'Incorrect Username or Password', login_response.data)
        self.assertIn(b'Sign in to start saving!', login_response.data)

    def test_get_forgot_password_success(self):
        # Test successful GET request to /forgotpassword/
        fPassword_response = self.app.get('/forgotpassword/')
        self.assertEqual(fPassword_response.status_code, 200)
        self.assertIn(b'Enter your Email', fPassword_response.data)

    def test_get_forgot_password_failure_already_logged_in(self):
        # Test GET request for user already logged in
        # Login test user
        login_response = self.app.post('/login/', data=self.test_user, follow_redirects=True)
        self.assertEqual(login_response.status_code, 200)

        # Test GET request to /forgotpassword/
        fPassword_response = self.app.get('/forgotpassword/', follow_redirects=True)
        self.assertEqual(fPassword_response.status_code, 200)

        # User is redirected back to dashboard
        self.assertIn(b'Looks like you&#39;re already logged in!', fPassword_response.data)

    def test_post_forgot_password_success(self):
        # Test POST request to /forgotpassword/ with correct email
        fPassword_response = self.app.post('/forgotpassword/', data={'email_forgot': 'test@test.com'}, follow_redirects=True)
        self.assertEqual(fPassword_response.status_code, 200)
        self.assertIn(b'Please answer your Security Questions', fPassword_response.data)

    def test_post_forgot_password_failure_incorrect_email(self):
        # Test POST request to /forgotpassword/ with invalid email
        fPassword_response = self.app.post('/forgotpassword/', data={'email_forgot': 'test123@invalid.com'}, follow_redirects=True)
        self.assertEqual(fPassword_response.status_code, 200)
        self.assertIn(b'The email provided was not found, please try again', fPassword_response.data)

    def test_get_forgot_questions_success(self):
        # Test successful GET request to /fogotQuestions/
        fQuestions_response = self.app.get('/forgotQuestions/?email=test@test.com')
        self.assertEqual(fQuestions_response.status_code, 200)
        self.assertIn(b'Please answer your Security Questions', fQuestions_response.data)

    def test_get_forgot_questions_failure(self):
        # Tests GET request to /forgotQuestions/ while trying to bypass /forgotpassword/
        fQuestions_response = self.app.get('/forgotQuestions/', follow_redirects=True)
        self.assertEqual(fQuestions_response.status_code, 200)

        # User is redirected to index
        self.assertIn(b'Welcome to Balanced Budgets', fQuestions_response.data)

    def test_post_forgot_questions_success(self):
        # Tests successful POST request to /forgotQuestions/
        fQuestions_response = self.app.post('/forgotQuestions/?email=test@test.com', data={'question1': 'test1', 'question2': 'test2'}, follow_redirects=True)
        self.assertEqual(fQuestions_response.status_code, 200)
        self.assertIn(b'Please Enter a New Password', fQuestions_response.data)

    def test_post_forgot_questions_failure_wrong_question(self):
        # Tests POST request to /forgotQuestions/ with wrong question answers
        fQuestions_response = self.app.post('/forgotQuestions/?email=test@test.com', data={'question1': 'invalid1', 'question2': 'invalid2'}, follow_redirects=True)
        self.assertEqual(fQuestions_response.status_code, 200)
        self.assertIn(b'Answers were not correct. Please try again', fQuestions_response.data)

    def test_get_reset_password_success(self):
        # Test successful GET request to /resetPassword/
        fReset_response = self.app.get('/resetPassword/?email=test@test.com')
        self.assertEqual(fReset_response.status_code, 200)
        self.assertIn(b'Please Enter a New Password', fReset_response.data)

    def test_post_reset_password_success(self):
        # Test successful POST request to /resetPassword/
        fReset_response = self.app.post('/resetPassword/?email=test@test.com', data={'newPassword': 'test', 'confirmPassword': 'test'}, follow_redirects=True)
        self.assertEqual(fReset_response.status_code, 200)

        # User is redirected to Login
        self.assertIn(b'Sign in to start saving!', fReset_response.data)
        self.assertIn(b'Your Password has been Updated!', fReset_response.data)

    def test_post_reset_password_failure_mismatched_passwords(self):
        # Test POST request to /resetPassword/ with different new passwords
        fReset_response = self.app.post('/resetPassword/?email=test@test.com', data={'newPassword': 'test', 'confirmPassword': 'invalid'})
        self.assertEqual(fReset_response.status_code, 200)
        self.assertIn(b'Oops, your passwords did not match!', fReset_response.data)

    def test_get_signup_success(self):
        # Test successful GET request to /signup/ route
        fSignup_response = self.app.get('/signup/')
        self.assertEqual(fSignup_response.status_code, 200)
        self.assertIn(b'Sign Up to Balanced Budgets', fSignup_response.data)

if __name__ == '__main__':
    unittest.main()