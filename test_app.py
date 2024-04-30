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

    def test_dashboard_route(self):
        # Login test user
        login_response = self.app.post('/login/', data=self.test_user, follow_redirects=True)
        self.assertEqual(login_response.status_code, 200)

        # Test GET request to /dashboard/ route
        dashboard_response = self.app.get('/dashboard/')
        self.assertEqual(dashboard_response.status_code, 200)
        self.assertIn(b'Budgeting Dashboard', dashboard_response.data)

    def test_get_login_page_success(self):
        # Test GET request to /login/ route
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
        # Test POST request to forgot password with correct email
        fPassword_response = self.app.post('/forgotpassword/', data={'email_forgot': 'test@test.com'}, follow_redirects=True)
        self.assertEqual(fPassword_response.status_code, 200)
        self.assertIn(b'Please answer your Security Questions', fPassword_response.data)

    def test_post_forgot_password_failure_incorrect_email(self):
        # Test POST request to /forgotpassword/ with invalid email
        fPassword_response = self.app.post('/forgotpassword/', data={'email_forgot': 'test123@invalid.com'}, follow_redirects=True)
        self.assertEqual(fPassword_response.status_code, 200)
        self.assertIn(b'The email provided was not found, please try again', fPassword_response.data)

if __name__ == '__main__':
    unittest.main()