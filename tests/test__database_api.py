import collections
from unittest import TestCase

import mongomock


class DatabaseAPITest(TestCase):

    def setUp(self):
        self.database = mongomock.MongoClient().somedb

    def test__get_collection_by_attribute_underscore(self):
        with self.assertRaises(AttributeError) as err_context:
            self.database._users  # pylint: disable=pointless-statement

        self.assertIn("Database has no attribute '_users'", str(err_context.exception))

        # No problem accessing it through __get_item__.
        self.database['_users'].insert_one({'a': 1})
        self.assertEqual(1, self.database['_users'].find_one().get('a'))

    def test__collection_names(self):
        self.database.a.create_index('foo')
        self.database['system.bar'].create_index('foo')
        self.assertEqual(['a'], self.database.collection_names(include_system_collections=False))

    def test__list_collection_names(self):
        self.database.test1.create_index('foo')
        self.assertEqual(['test1'], self.database.list_collection_names())

    def test__session(self):
        with self.assertRaises(NotImplementedError):
            self.database.list_collection_names(session=1)
        with self.assertRaises(NotImplementedError):
            self.database.drop_collection('a', session=1)
        with self.assertRaises(NotImplementedError):
            self.database.create_collection('a', session=1)
        with self.assertRaises(NotImplementedError):
            self.database.dereference(_DBRef('somedb', 'a', 'b'), session=1)

    def test__command_ping(self):
        self.assertEqual({'ok': 1}, self.database.command({'ping': 1}))

    def test__command_ping_string(self):
        self.assertEqual({'ok': 1}, self.database.command('ping'))

    def test__command_fake_ping_string(self):
        with self.assertRaises(NotImplementedError):
            self.assertEqual({'ok': 1}, self.database.command('a_nice_ping'))

    def test__command(self):
        with self.assertRaises(NotImplementedError):
            self.database.command({'count': 'user'})

    def test__repr(self):
        self.assertEqual(
            "Database(mongomock.MongoClient('localhost', 27017), 'somedb')", repr(self.database))

    def test__rename_unknown_collection(self):
        with self.assertRaises(mongomock.OperationFailure):
            self.database.rename_collection('a', 'b')

    def test__dereference(self):
        self.database.a.insert_one({'_id': 'b', 'val': 42})
        doc = self.database.dereference(_DBRef('somedb', 'a', 'b'))
        self.assertEqual({'_id': 'b', 'val': 42}, doc)

        self.assertEqual(None, self.database.dereference(_DBRef('somedb', 'a', 'a')))
        self.assertEqual(None, self.database.dereference(_DBRef('somedb', 'b', 'b')))

        with self.assertRaises(ValueError):
            self.database.dereference(_DBRef('otherdb', 'a', 'b'))

        with self.assertRaises(TypeError):
            self.database.dereference('b')

    def test__get_collection(self):
        with self.assertRaises(NotImplementedError):
            self.database.get_collection('a', read_concern=3)


_DBRef = collections.namedtuple('DBRef', ['database', 'collection', 'id'])
