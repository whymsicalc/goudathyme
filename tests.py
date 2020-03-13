
from model import connect_to_db, db, example_data 
from server import app
from flask import session
import os
from unittest import TestCase

        
def use_db(db_uri, db, app):
    """Decorate a TestCase class to set up database connections.
    Since we use Flask-SQLAlchemy to facilitate database connections, this
    decorator needs:
    - db_uri: the database URI
    - db: A SQLAlchemy instance
    - app: A Flask instance
    """
    def inner(cls):
        temp_init = cls.__init__
        temp_setup = cls.setUp
        temp_teardown = cls.tearDown
        def init_db(self, *args) -> None:
            if not getattr(self, 'app', None):
                self.app = app
            self.app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
            self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
            if not getattr(self, 'db', None):
                self.db = db
            self.db.app = self.app
            self.db.init_app(self.app)
            temp_init(self, *args)
        cls.__init__ = init_db
        def setup_db(self) -> None:
            self.connection = db.engine.connect()
            self.trans = self.connection.begin()
            self.session = db.session
            temp_setup(self)
        cls.setUp = setup_db
        def teardown_db(self) -> None:
            self.session.close()
            self.trans.rollback()
            self.db.drop_all()
            self.connection.close()
            temp_teardown(self)
        cls.tearDown = teardown_db
        return cls
    return inner

class FlaskTestsBasic(TestCase):
    """Flask tests."""

    def setUp(self):
        """Things to do before every test."""

        # Get the Flask test client
        self.client = app.test_client()

        # Show Flask errors that happen during tests
        app.config['TESTING'] = True

    def test_index(self):
        """Test homepage."""

        result = self.client.get("/")
        self.assertIn(b"Hello! Welcome to <br>Gouda Thyme!</h1><br>", result.data)

    def test_registration(self):
        """Test registration page."""

        result = self.client.get("/register")
        self.assertIn(b"Create an Account", result.data)

@use_db('postgres:///testdb', db, app)
class FlaskTestsDatabase(TestCase):
    """Flask tests that use the database."""

    def setUp(self):
        """Things to do before every test."""

        self.client = self.app.test_client()

        # Create tables and add sample data
        self.db.create_all()
        example_data()

    def test_login(self):
        """Test login."""

        result = self.client.post("/login",
                                  data={"username": "janedoe", "password": "abc123"},
                                  follow_redirects=True)
        self.assertIn(b"Hello there", result.data)

    def test_wrong_login(self):
        """Test login with wrong password."""

        result = self.client.post("/login",
                                  data={"username": "janedoe", "password": "abc"},
                                  follow_redirects=True)
        self.assertIn(b'<h4 class="card-title text-center white">Sign in</h4>', result.data)

    def test_login_without_account(self):
        """Test login without an account."""

        result = self.client.post("/login",
                                  data={"username": "fakeuser", "password": "123"},
                                  follow_redirects=True)
        self.assertIn(b"Create an Account", result.data)

    def test_create_account(self):
        """Test account creation."""

        result = self.client.post("/register",
                                  data={"fname": "John", "lname": "Smith", 
                                        "email": "john@gmail.com", "form_phone": None, 
                                        "username": "johnsmith", "password": "123"},
                                  follow_redirects=True)
        self.assertIn(b"Hello there", result.data)


@use_db('postgres:///testdb', db, app)
class FlaskTestsLoggedIn(TestCase):
    """Flask tests with user logged in to session."""

    def setUp(self):
        """Things to do before every test."""

        self.client = self.app.test_client()
        self.app.config['SECRET_KEY'] = os.environ['SECRET_KEY'] 

        self.db.create_all()
        example_data()

        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = 1

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
        self.assertIn(b'<h4 class="card-title text-center white">Sign in</h4>', result.data)


@use_db('postgres:///testdb', db, app)
class FlaskTestsLogInLogOut(TestCase):
    """Test log in and log out."""

    def setUp(self):
        """Before every test"""

        self.client = self.app.test_client()

        self.db.create_all()
        example_data()

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
            self.assertIn(b'Hello! Welcome to <br>Gouda Thyme!</h1><br>', result.data)


if __name__ == "__main__":
    import unittest

    unittest.main()
