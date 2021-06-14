from app import app
import unittest


class FlaskTestCase(unittest.TestCase):
    # Executed prior to each test
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['MYSQL_HOST'] = 'localhost'
        app.config['MYSQL_USER'] = 'root'
        app.config['MYSQL_PASSWORD'] = 'root'
        app.config['MYSQL_PORT'] = 3306
        app.config['MYSQL_DB'] = 'librarytestdb'
        app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
        app.secret_key = "secrettest"

    def tearDown(self):
        pass

    # Test that index page loads correctly
    def test_index(self):
        tester = app.test_client(self)
        response = tester.get('/', content_type='html/text')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b'Library Management System' in response.data)

    # Test that members page loads correctly
    def test_members(self):
        tester = app.test_client(self)
        response = tester.get('/members', content_type='html/text')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b'Members' in response.data)

    # Test that books page loads correctly
    def test_books(self):
        tester = app.test_client(self)
        response = tester.get('/books', content_type='html/text')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b'Books' in response.data)

    # Test that transactions page loads correctly
    def test_transactions(self):
        tester = app.test_client(self)
        response = tester.get('/transactions', content_type='html/text')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b'Transactions' in response.data)

    # Test that reports page loads correctly
    def test_reports(self):
        tester = app.test_client(self)
        response = tester.get('/reports', content_type='html/text')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b'Reports' in response.data)

    # Test that search page loads correctly
    def test_search(self):
        tester = app.test_client(self)
        response = tester.get('/search_book', content_type='html/text')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b'Search' in response.data)

    # Test that add member form works as expected with valid input
    def test_add_member(self):
        tester = app.test_client(self)
        response = tester.post(
            '/add_member',
            data=dict(name="admin", email="admin@admin.com"),
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'New Member Added', response.data)

    # Test that add member form works as expected with invalid input
    def test_add_member_invalid(self):
        tester = app.test_client(self)
        response = tester.post(
            '/add_member',
            data=dict(name="a", email="a"),
            follow_redirects=True
        )
        self.assertIn(b'Field must be', response.data)

    # Test that edit member form works as expected with valid input
    def test_edit_member(self):
        tester = app.test_client(self)
        response = tester.post(
            '/edit_member/1',
            data=dict(name="adminedited", email="admin@edited.com"),
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Member Updated', response.data)

    # Test that edit member form works as expected with invalid input
    def test_edit_member_invalid(self):
        tester = app.test_client(self)
        response = tester.post(
            '/edit_member/1',
            data=dict(name="a", email="a"),
            follow_redirects=True
        )
        self.assertIn(b'Field must be', response.data)

    # Test that add book form works as expected with invalid input
    def test_add_book_invalid(self):
        tester = app.test_client(self)
        response = tester.post(
            '/add_book',
            data=dict(id="1", title="a"),
            follow_redirects=True
        )
        self.assertIn(b'Field must be', response.data)

    # Test that edit book form works as expected with invalid input
    def test_edit_book_invalid(self):
        tester = app.test_client(self)
        response = tester.post(
            '/edit_book/1',
            data=dict(id="1"),
            follow_redirects=True
        )
        self.assertIn(b'Field must be', response.data)

    # Test that import books form works as expected with invalid input
    def test_import_books_invalid(self):
        tester = app.test_client(self)
        response = tester.post(
            '/import_books',
            data=dict(no_of_books="1"),
            follow_redirects=True
        )
        self.assertIn(b'Number must be', response.data)

    # Test that issue book form works as expected with invalid input
    def test_issue_book_invalid(self):
        tester = app.test_client(self)
        response = tester.post(
            '/issue_book',
            data=dict(book_id="1", member_id="1"),
            follow_redirects=True
        )
        self.assertIn(b'Number must be', response.data)


if __name__ == '__main__':
    unittest.main()
