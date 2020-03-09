from unittest import TestCase
from server import app
from model import connect_to_db, db, example_data
from flask import session
import os
        
# Connect to test database
connect_to_db(app, "postgresql:///testdb")

class FlaskTestsBasic(TestCase):
    """Flask tests."""

    def setUp(self):
        """Things to do before every test."""

        # Get the Flask test client
        self.client = app.test_client()

        # Show Flask errors that happen during tests
        app.config['TESTING'] = True

    def test_index(self):
        """Test homepage page."""

        result = self.client.get("/")
        self.assertIn(b"Welcome to More Thyme", result.data)

    def test_registration(self):
        """Test registration page."""

        result = self.client.get("/register")
        self.assertIn(b"Create an Account", result.data)


class FlaskTestsDatabase(TestCase):
    """Flask tests that use the database."""

    def setUp(self):
        """Things to do before every test."""

        # Get the Flask test client
        self.client = app.test_client()
        app.config['TESTING'] = True

        # Create tables and add sample data
        db.create_all()
        example_data()

    def tearDown(self):
        """Do at end of every test."""

        db.session.remove()
        db.drop_all()
        db.engine.dispose()

    def test_login(self):
        """Test login page."""

        result = self.client.post("/login",
                                  data={"username": "janedoe", "password": "abc123"},
                                  follow_redirects=True)
        self.assertIn(b"Hello there", result.data)

    def test_wrong_login(self):
        """Test login with wrong password."""

        result = self.client.post("/login",
                                  data={"username": "janedoe", "password": "abc"},
                                  follow_redirects=True)
        self.assertIn(b"Sign In", result.data)

    def test_login_without_account(self):
        """Test login without an account."""

        result = self.client.post("/login",
                                  data={"username": "fakeuser", "password": "123"},
                                  follow_redirects=True)
        self.assertIn(b"Create an Account", result.data)

    def test_create_account(self):
        """Test account creation."""

        result = self.client.post("/register",
                                  data={"fname": "John", "lname": "Smith", "email": "john@gmail.com", "form_phone": None, "username": "johnsmith", "password": "123"},
                                  follow_redirects=True)
        self.assertIn(b"Hello there", result.data)


class FlaskTestsLoggedIn(TestCase):
    """Flask tests with user logged in to session."""

    def setUp(self):
        """Things to do before every test."""

        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = os.environ['SECRET_KEY'] 

        self.client = app.test_client()

        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = 1

        db.create_all()
        example_data()

    def tearDown(self):
        """Do at end of every test."""

        db.session.remove()
        db.drop_all()
        db.engine.dispose()

    def test_my_items_page(self):
        """Test my items page."""

        result = self.client.get("/my-items/1")
        self.assertIn(b"Hello there,", result.data)


class FlaskTestsLoggedOut(TestCase):
    """Flask tests with user logged in to session."""

    def setUp(self):
        """Stuff to do before every test."""

        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_logged_out_items_page(self):
        """Test that user can't see my items page when logged out."""

        result = self.client.get("/my-items/1", follow_redirects=True)
        self.assertNotIn(b"Hello there", result.data)
        self.assertIn(b"Sign In", result.data)


class FlaskTestsLogInLogOut(TestCase):
    """Test log in and log out."""

    def setUp(self):
        """Before every test"""

        app.config['TESTING'] = True
        self.client = app.test_client()

        db.create_all()
        example_data()

    def tearDown(self):
        """Do at end of every test."""

        db.session.remove()
        db.drop_all()
        db.engine.dispose()

    def test_login(self):
        """Test log in form.

        Unlike login test above, 'with' is necessary here in order to refer to session.
        """

        with self.client as c:
            result = c.post('/login',
                            data={"username": "janedoe", "password": "abc123"},
                            follow_redirects=True
                            )
            self.assertEqual(session['user_id'], 1)
            self.assertIn(b"Hello there", result.data)

    def test_logout(self):
        """Test logout route."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = 1

            result = self.client.get('/logout', follow_redirects=True)

            self.assertNotIn(b'user_id', session)
            self.assertIn(b'Welcome to More Thyme', result.data)


if __name__ == "__main__":
    import unittest

    unittest.main()
