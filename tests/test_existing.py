"""已有接口的核心、边界及错误路径。"""
import unittest,tempfile
from pathlib import Path
from lake.storage import read_source,Objects,digest

class StorageTests(unittest.TestCase):
    def test_source_and_corruption(self):
        value=read_source()
        with tempfile.TemporaryDirectory() as d:
            o=Objects(d);key=o.put(value);self.assertEqual(o.get(key),value)
            self.assertEqual(o.put(value),key)
            Path(d,key).write_bytes(b'bad')
            with self.assertRaises(ValueError):o.get(key)
    def test_bad_object_identity(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):Objects(d).get('../bad')


from lake.score import score,physical_key
from lake.indexio import Table,AttributeIndex

class FeatureTests(unittest.TestCase):
    def test_signed_exact_score(self):
        w={'a':2,'b':-3};self.assertEqual(score({'a':4,'b':2},w),2)
        self.assertIsNone(score({'a':4},w))
        self.assertEqual(score({'a':2**62,'b':0},w),2**63)
        with self.assertRaises(ValueError):score({'a':True,'b':0},w)
    def test_independent_order_and_lookup(self):
        t=Table(read_source()['rows']);a=AttributeIndex(t,'raw','asc');b=AttributeIndex(t,'stock','desc')
        p=a.page(0,1,t.digest,a.digest);self.assertEqual(p['rows'][0]['row_id'],'a');self.assertFalse(p['complete'])
        self.assertEqual(t.get('c',t.digest)['freight'],40);self.assertEqual(t.gets,['c'])
        self.assertEqual(b.page(0,1,t.digest,b.digest)['rows'][0]['value'],3)
        with self.assertRaises(ValueError):a.page(0,1,'old',a.digest)
