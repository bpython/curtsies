import unittest
import fmtstr

class TestFmtStrInitialization(unittest.TestCase):
    def test_bad(self):
        # Can't specify fg or bg color two ways
        self.assertRaises(ValueError, fmtstr.FmtStr, 'hello', 'blue', {'fg':30})
        self.assertRaises(ValueError, fmtstr.FmtStr, 'hello', 'on_blue', {'bg':40})
        # Only specific fg and bg colors are allowed
        self.assertRaises(ValueError, fmtstr.FmtStr, 'hello', {'bg':30})
        self.assertRaises(ValueError, fmtstr.FmtStr, 'hello', {'fg':40})
        # Only existing xforms can be used in kwargs
        self.assertRaises(ValueError, fmtstr.FmtStr, 'hello', 'make it big')

class TestFmtStr(unittest.TestCase):

    def setUp(self):
        self.s = fmtstr.FmtStr('hello!', 'upper', fg='red')

    def test_length(self):
        self.assertEqual(len(self.s), len(self.s.string))

    #def test_sample(self):
        #with self.assertRaises(ValueError):
            #random.sample(self.seq, 20)
        #for element in random.sample(self.seq, 5):
            #self.assertTrue(element in self.seq)

if __name__ == '__main__':
    unittest.main()
