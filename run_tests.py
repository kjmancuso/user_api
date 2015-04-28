# -*- coding: utf-8 -*-
import json
import unittest

import user_api

# Test data
jsmith = {'first_name': 'Joe',
          'last_name': 'Smith',
          'userid': 'jsmith',
          'groups': ['admins', 'users']}

john = {'first_name': 'Johnnie',
        'last_name': 'Johnson',
        'userid': 'jjohnson',
        'groups': ['users']}

johnson = {'first_name': 'Jøhnnie',
           'last_name': 'Jöhnson',
           'userid': 'hoser',
           'groups': ['hosers', 'users']}


# Tests
class UserAPITest(unittest.TestCase):
    def setUp(self):
        user_api.app.config['TESTING'] = True
        self.app = user_api.app.test_client()

    def tearDown(self):
        pass

    # Simulate proper JSON posting
    def jpost(self, url, payload):
        rv = self.app.post(url, data=json.dumps(payload),
                           content_type='application/json')
        return rv

    def jput(self, url, payload):
        rv = self.app.put(url, data=json.dumps(payload),
                          content_type='application/json')
        return rv

    # Some (mostly negative) tests
    def test_malformed_user(self):
        jsmith_broken = jsmith.copy()
        jsmith_broken.pop('last_name')
        rv = self.jpost('/users', jsmith_broken)

        self.assertEquals(rv.status_code, 400)
        self.assertIn('Malformed user entity', rv.data)

    def test_get_missing_user(self):
        rv = self.app.get('/users/4chanmoot')
        self.assertEquals(rv.status_code, 404)

    def test_delete_missing_user(self):
        rv = self.app.delete('/users/4chanmoot')
        self.assertEquals(rv.status_code, 404)

    def test_replace_missing_user(self):
        rv = self.jput('/users/4chanmoot', jsmith)
        self.assertEquals(rv.status_code, 404)

    def test_missing_group(self):
        rv = self.app.get('/groups/peanutbutter')
        self.assertEquals(rv.status_code, 404)

    # Order dependant tests
    def test_010_create_user(self):
        rv = self.jpost('/users', jsmith)

        self.assertEquals(rv.status_code, 200)
        self.assertEquals(json.loads(rv.data), jsmith)

    def test_011_create_other_user(self):
        rv = self.jpost('/users', john)
        self.assertEquals(rv.status_code, 200)
        self.assertEquals(json.loads(rv.data), john)

    # TODO Proper unicode handling
    # def test_015_create_unicode_user(self):
    #    rv = self.jpost('/users', johnson)
    #    print rv.data

    def test_020_create_existing_user(self):
        rv = self.jpost('/users', jsmith)
        self.assertEquals(rv.status_code, 400)
        self.assertIn('User already exists', rv.data)

    def test_030_retrieve_user(self):
        rv = self.app.get('/users/jsmith')
        self.assertEquals(rv.status_code, 200)
        self.assertEquals(json.loads(rv.data), jsmith)

    def test_040_replace_user(self):
        jsmith_mod = jsmith.copy()
        jsmith_mod['first_name'] = 'Johnnie'
        rv = self.jput('/users/jsmith', jsmith_mod)
        self.assertEquals(rv.status_code, 200)
        self.assertEquals(json.loads(rv.data), jsmith_mod)

    def test_050_delete_user(self):
        rv = self.app.delete('/users/jsmith')
        self.assertEquals(rv.status_code, 200)
        self.assertIn('User jsmith has been deleted', rv.data)

    def test_060_create_group(self):
        p = {'name': 'flowerpot'}
        rv = self.jpost('/groups', p)
        self.assertEquals(rv.status_code, 200)

    def test_070_create_existing_group(self):
        p = {'name': 'flowerpot'}
        rv = self.jpost('/groups', p)
        self.assertEquals(rv.status_code, 400)
        self.assertIn('Group flowerpot already exists', rv.data)

    def test_080_get_group_membership(self):
        rv = self.app.get('/groups/users')
        self.assertEquals(rv.status_code, 200)
        self.assertEquals(json.loads(rv.data), ['jjohnson'])

    def test_090_replace_group_membership(self):
        rv = self.jput('/groups/users', ['jjohnson', 'jsmith'])
        self.assertEquals(rv.status_code, 200)
        self.assertEquals(json.loads(rv.data), ['jjohnson', 'jsmith'])

    def test_100_delete_group(self):
        rv = self.app.delete('/groups/users')
        self.assertEquals(rv.status_code, 200)


if __name__ == '__main__':
    unittest.main()
