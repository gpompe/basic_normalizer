import unittest
from unittest.mock import patch, mock_open
from textwrap import dedent

import normalizer as norm


class TestNormalization(unittest.TestCase):
    def setUp(self):
        norm.loadData()

    def test_replacesubstitutes(self):
        """should replace subsitutes"""
        self.assertEqual(norm.normalize("Nov 1st I weighed 90 kgs. total"),"November 1st I weighed 90 kilograms total")
        self.assertEqual(norm.normalize("I shared it on FB w/ friends, ie: you"),"I shared it on Facebook with friends, for example : you")


    def test_contractions(self):
        """should expand contractions"""
        self.assertEqual(norm.normalize("I'm on the yelow zebra"),"I am on the yellow zebra")
        self.assertEqual(norm.normalize("I'll listen to y'all"),"I will listen to you all")
        self.assertEqual(norm.normalize("do n't make it right"),"do not make it right")
        self.assertEqual(norm.normalize("it's all good"),"it is all good")


    def test_swapping(self):
        """should swap british / canadian words"""
        self.assertEqual(norm.normalize("armour axe coloured gold"),"armor ax colored gold")


    def test_spelling(self):
        """should fix spelling"""
        self.assertEqual(norm.normalize("are we sceduled thrsday for teh restraunt"),"are we scheduled Thursday for the restaurant")


    def test_expand(self):
        """should expand txt speak"""
        self.assertEqual(norm.normalize("n"),"~no")
        self.assertEqual(norm.normalize("lol"),"~emolaugh")
        self.assertEqual(norm.normalize("haha"),"~emolaugh")
        self.assertEqual(norm.normalize(":)"),"~emohappy")


    def test_cleancase(self):
        """should clean this"""
        self.assertEqual(norm.normalize("Well , I could not help it, could I"),"I could not help it, could I")


    def test_notremoval(self):
        """should not remove +"""
        self.assertEqual(norm.normalize("3+4=7"),"3+4=7")


    def test_extraspaces(self):
        """should remove extra spaces"""
        self.assertEqual(norm.normalize("this    is     spaced     out"),"this is spaced out")


    def test_removepunct(self):
        """should remove punct"""
        self.assertEqual(norm.normalize("why do i care?"),"why do I care")


    def test_fixnumbers(self):
        """Fix numbers"""
        self.assertEqual(norm.normalize("how much is 1,000.00"),"how much is 1000.00")


    def test_wordcombo(self):
        """Spell Fix 2 word combo"""
        self.assertEqual(norm.normalize("hwo do you"),"how do you")
        self.assertEqual(norm.normalize("hwo is you"),"who is you")



    def test_asciichars(self):
        """Fix ASCII characters"""
        self.assertEqual(norm.normalize("What’s up"),"what is up")
        self.assertEqual(norm.normalize("What's up"),"what is up")
        self.assertEqual(norm.normalize("I said “shut up”"),'I said "shut up"')
        self.assertEqual(norm.normalize("œ"),'')
