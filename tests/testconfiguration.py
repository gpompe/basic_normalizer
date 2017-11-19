import unittest
from unittest.mock import patch, mock_open
from textwrap import dedent

import normalizer


class TestConfiguration(unittest.TestCase):

    def setUp(self):
        file_content = dedent("""
             !>  # sets bit and deletes
             ,>  # remove useless end punctuation
             .>  # set bits remove useless end punctuation
             ;>  # remove useless end punctuation
             ->  # remove useless end punctuation
             ?>
             <-  # remove starting hypen broken off from prior sentence
             <,  # remove starting comma (maybe words before it got deleted)
             <.  # erase leading period
             i I
             -_-
             """).strip()
        # Instantiate the object where the data is file_content
        self.mock_open = mock_open(read_data = file_content)
        # And add the omitted __iter__ &amp;amp;amp; __next__ methods
        self.mock_open.return_value.__iter__ = lambda self:self
        self.mock_open.return_value.__next__ = lambda self: next(iter(self.readline, ''))

    def test_precleaning(self):
        self.assertEqual(normalizer.clean("This is a normal sentence.",normalizer.repreclean()), "This is a normal sentence.","No cleaning required")
        self.assertEqual(normalizer.clean("This     is    a   normal   sentence.",normalizer.repreclean()), "This is a normal sentence.","Failed to remove extra spaces")
        self.assertEqual(normalizer.clean("This \tis\ta normal\tsentence.",normalizer.repreclean()), "This is a normal sentence.","Failed to remove extra spaces")
        self.assertEqual(normalizer.clean("This is a ‘normal’ sentence.",normalizer.repreclean()), "This is a 'normal' sentence.","Failed to replace single quotes")
        self.assertEqual(normalizer.clean("This is a ”normal“ sentence.",normalizer.repreclean()), 'This is a "normal" sentence.',"Failed to replace double quotes")
        self.assertEqual(normalizer.clean("This is a –normal— sentence.",normalizer.repreclean()), 'This is a -normal- sentence.',"Failed to replace dashes")
        self.assertEqual(normalizer.clean("This     is a –normal— ”normal“ ‘normal’ \tsentence.",normalizer.repreclean()), 'This is a -normal- "normal" \'normal\' sentence.',"Failed to fully clean the phrase")
        self.assertEqual(normalizer.clean("3+5+6",normalizer.repreclean()), "3<plus>5<plus>6","Failed to replace plus sign")

    def test_quotemeta(self):
        ''' quotemeta: This test the function that escapes characters within the regex'''
        self.assertEqual(normalizer.quotemeta("!"), r"\!","Failed to escape characters")
        self.assertEqual(normalizer.quotemeta("+++"), r"\+\+\+","Failed to escape characters")

    def test_readsubstitutes(self):

        self.maxDiff=None
        with patch('builtins.open', self.mock_open):
            self.assertEqual(normalizer.readSubstitutes("_sys","systemessent.txt"), { '!>': [ { 're': "(\\W+|^)\!$", 'r': '\\g<1>' }, { 're': "\!$", 'r': '' } ], \
                  ',>': [ { 're': "(\\W+|^),$", 'r': '\\g<1>' }, { 're': ",$", 'r': '' } ], \
                  '.>': [ { 're': "(\\W+|^)\.$", 'r': '\\g<1>' }, { 're': "\.$", 'r': '' } ], \
                  ';>': [ { 're': "(\\W+|^);$", 'r': '\\g<1>' }, { 're': ";$", 'r': '' } ], \
                  '->': [ { 're': "(\\W+|^)-$", 'r': '\\g<1>' }, { 're': "-$", 'r': '' } ], \
                  '?>': [ { 're': "(\\W+|^)\?$", 'r': '\\g<1>' }, { 're': "\?$", 'r': '' } ], \
                  '<-': [ { 're': "^-(\\W+|$)", 'r': '\\g<1>' } ], \
                  '<,': [ { 're': "^,(\\W+|$)", 'r': '\\g<1>' } ], \
                  '<.': [ { 're': "^\.(\\W+|$)", 'r': '\\g<1>' } ], \
                  'i': [ { 're': "(\\W+|^)i(\\W+|$)", 'r': '\\g<1>I\\g<2>' } ], \
                  '-_-': [ { 're': "(\\W+|^)- -(\\W+|$)", 'r': '\\g<1>\\g<2>' } ] },"Failed to read Substitutes")

    def test_readsubstitutes_error(self):
        """ readSubtitutes: check for file not found"""
        with self.assertRaises(FileNotFoundError):
            normalizer.readSubstitutes("_sys","systemessent.txt")

    def test_lineHandle(self):
        self.assertEqual(normalizer.lineHandle("_sys","!>",""),[{'re':"(\\W+|^)\!$",'r':"\\g<1>"},{'re':"\\!$", 'r':""}] ,"Failed to handle line ending tag")
        self.assertEqual(normalizer.lineHandle("_sys","-_-",""),[{ 're': "(\\W+|^)- -(\\W+|$)", 'r': '\\g<1>\\g<2>' }] ,"Failed to handle line middle tag")
        self.assertEqual(normalizer.lineHandle("_sys","i","I"),[{ 're': "(\\W+|^)i(\\W+|$)", 'r': '\\g<1>I\\g<2>' }] ,"Failed to handle line middle tag with replace")
        self.assertEqual(normalizer.lineHandle("_sys","<.",""),[{ 're': "^\\.(\\W+|$)", 'r': '\\g<1>' }] ,"Failed to handle line starting tag")

    def test_isloaded(self):

        self.assertFalse(normalizer.is_loaded(),"Failed to dectect empty data")

        with patch('builtins.open', self.mock_open):
            normalizer.loadData()

        self.assertTrue(normalizer.is_loaded(),"Failed to dectect loaded data")

        normalizer.clearData()
        self.assertFalse(normalizer.is_loaded(),"Failed to dectect empty data")


if __name__ == '__main__':
    unittest.main()
