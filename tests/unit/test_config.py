import tempfile
import unittest

from haproxy.config import parse_extra_bind_settings, parse_extra_frontend_settings, getExtendedEnv


class ParseExtraBindSettings(unittest.TestCase):
    def test_parse_extra_bind_settings(self):
        self.assertEqual({}, parse_extra_bind_settings(""))
        self.assertEqual({"80": "name http"}, parse_extra_bind_settings("80:name http"))
        self.assertEqual({"80": "name  http"}, parse_extra_bind_settings(" 80 : name  http  "))
        self.assertEqual({"80": "name http", "443": "accept-proxy"},
                         parse_extra_bind_settings(" 443:accept-proxy  , 80:name http "))
        self.assertEqual({"80": "name, http", "443": "accept,-proxy"},
                         parse_extra_bind_settings(" 443:accept\,-proxy, 80:name\, http "))


class ParseExtraFrontendSettings(unittest.TestCase):
    def test_parse_extra_frontend_settings(self):
        self.assertEqual({}, parse_extra_frontend_settings(""))
        self.assertEqual({}, parse_extra_frontend_settings({}))
        tf = tempfile.NamedTemporaryFile();
        tf.write("reqadd file_header value99")
        tf.flush()

        envvars = {"EXTRA_FRONTEND_SETTINGS_443": " reqadd header1 value1, reqadd header2 va\,lue2,"
                                                  "  reqadd header3 value3 ",
                   "EXTRA_FRONTEND_SETTINGS_FILE_443": tf.name,
                   "EXTRA_FRONTEND_SETTINGS_80": "reqadd header4",
                   "EXTRA_FRONTEND_SETTINGS_8080": "",
                   "EXTRA_FRONTEND_SETTINGS_ABC": "reqadd header5",
                   "EXTRA_FRONTEND_SETTINGS_": "reqadd header6"}
        settings = {"443": ["reqadd file_header value99", "reqadd header1 value1", "reqadd header2 va,lue2",
                            "reqadd header3 value3"],
                    "80": ["reqadd header4"],
                    "8080": [""]}
        self.assertEqual(settings, parse_extra_frontend_settings(envvars))


class GetExtendedEnv(unittest.TestCase):
    def test_get_extended_env(self):
        self.assertEqual('', getExtendedEnv('FOO', envvars={}))
        self.assertEqual('baz', getExtendedEnv('FOO', envvars={}, default='baz'))
        self.assertEqual('', getExtendedEnv('FOO', envvars={'BAR': 'bar'}))
        self.assertEqual('foo', getExtendedEnv('FOO', envvars={'BAR': 'bar', 'FOO': 'foo'}))
        self.assertEqual('foo A,foo B', getExtendedEnv('FOO', envvars={'BAR': 'bar', 'FOO_A': 'foo A', 'FOO_B': 'foo B'}))
        self.assertEqual('foo B,foo', getExtendedEnv('FOO', envvars={'BAR': 'bar', 'FOO': 'foo', 'FOO_B': 'foo B'}))
        self.assertEqual('foo B# foo', getExtendedEnv('FOO', envvars={'BAR': 'bar', 'FOO': 'foo', 'FOO_B': 'foo B'}, joinWith='# '))
        self.assertEqual('foo A,foo B', getExtendedEnv('FOO', envvars={'BAR': 'bar', 'FOO_A': 'foo A', 'FOO_WEB-SERVICE_Number2': 'foo B'}))
