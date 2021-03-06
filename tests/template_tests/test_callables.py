from __future__ import unicode_literals

from unittest import TestCase

from django import template


class CallableVariablesTests(TestCase):

    def test_callable(self):

        class Doodad(object):
            def __init__(self, value):
                self.num_calls = 0
                self.value = value

            def __call__(self):
                self.num_calls += 1
                return {"the_value": self.value}

        my_doodad = Doodad(42)
        c = template.Context({"my_doodad": my_doodad})

        # We can't access ``my_doodad.value`` in the template, because
        # ``my_doodad.__call__`` will be invoked first, yielding a dictionary
        # without a key ``value``.
        t = template.Template('{{ my_doodad.value }}')
        self.assertEqual(t.render(c), '')

        # We can confirm that the doodad has been called
        self.assertEqual(my_doodad.num_calls, 1)

        # But we can access keys on the dict that's returned
        # by ``__call__``, instead.
        t = template.Template('{{ my_doodad.the_value }}')
        self.assertEqual(t.render(c), '42')
        self.assertEqual(my_doodad.num_calls, 2)

    def test_alters_data(self):

        class Doodad(object):
            alters_data = True

            def __init__(self, value):
                self.num_calls = 0
                self.value = value

            def __call__(self):
                self.num_calls += 1
                return {"the_value": self.value}

        my_doodad = Doodad(42)
        c = template.Context({"my_doodad": my_doodad})

        # Since ``my_doodad.alters_data`` is True, the template system will not
        # try to call our doodad but will use TEMPLATE_STRING_IF_INVALID
        t = template.Template('{{ my_doodad.value }}')
        self.assertEqual(t.render(c), '')
        t = template.Template('{{ my_doodad.the_value }}')
        self.assertEqual(t.render(c), '')

        # Double-check that the object was really never called during the
        # template rendering.
        self.assertEqual(my_doodad.num_calls, 0)

    def test_do_not_call(self):

        class Doodad(object):
            do_not_call_in_templates = True

            def __init__(self, value):
                self.num_calls = 0
                self.value = value

            def __call__(self):
                self.num_calls += 1
                return {"the_value": self.value}

        my_doodad = Doodad(42)
        c = template.Context({"my_doodad": my_doodad})

        # Since ``my_doodad.do_not_call_in_templates`` is True, the template
        # system will not try to call our doodad.  We can access its attributes
        # as normal, and we don't have access to the dict that it returns when
        # called.
        t = template.Template('{{ my_doodad.value }}')
        self.assertEqual(t.render(c), '42')
        t = template.Template('{{ my_doodad.the_value }}')
        self.assertEqual(t.render(c), '')

        # Double-check that the object was really never called during the
        # template rendering.
        self.assertEqual(my_doodad.num_calls, 0)

    def test_do_not_call_and_alters_data(self):
        # If we combine ``alters_data`` and ``do_not_call_in_templates``, the
        # ``alters_data`` attribute will not make any difference in the
        # template system's behavior.

        class Doodad(object):
            do_not_call_in_templates = True
            alters_data = True

            def __init__(self, value):
                self.num_calls = 0
                self.value = value

            def __call__(self):
                self.num_calls += 1
                return {"the_value": self.value}

        my_doodad = Doodad(42)
        c = template.Context({"my_doodad": my_doodad})

        t = template.Template('{{ my_doodad.value }}')
        self.assertEqual(t.render(c), '42')
        t = template.Template('{{ my_doodad.the_value }}')
        self.assertEqual(t.render(c), '')

        # Double-check that the object was really never called during the
        # template rendering.
        self.assertEqual(my_doodad.num_calls, 0)
