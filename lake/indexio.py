"""正文回查及独立属性有序访问接口。"""
from copy import deepcopy
from .storage import digest

class Table:
    def __init__(self,rows):
        self.rows=deepcopy(rows);self.by_id={r['row_id']:r for r in self.rows}
        if len(self.by_id)!=len(self.rows):raise ValueError('行身份重复')
        self.digest=digest(self.rows);self.gets=[];self.scans=0
    def get(self,row_id,expected_digest):
        if expected_digest!=self.digest:raise ValueError('正文版本不符')
        self.gets.append(row_id);return deepcopy(self.by_id[row_id])
    def scan(self,expected_digest):
        if expected_digest!=self.digest:raise ValueError('正文版本不符')
        for row in self.rows:self.scans+=1;yield deepcopy(row)

class AttributeIndex:
    def __init__(self,table,field,direction):
        if direction not in ('asc','desc'):raise ValueError('索引方向非法')
        self.table_digest=table.digest;self.field=field;self.direction=direction;self.events=[]
        rows=[r for r in table.rows if r.get(field) is not None]
        if any(type(r[field]) is not int for r in rows):raise ValueError('属性值非法')
        sign=1 if direction=='asc' else -1
        self.entries=sorted([{'row_id':r['row_id'],'value':r[field]} for r in rows],key=lambda r:(sign*r['value'],r['row_id'].encode()))
        self.digest=digest({'table':table.digest,'field':field,'direction':direction,'entries':self.entries})
    def page(self,offset,limit,table_digest,index_digest,bound=True):
        if table_digest!=self.table_digest or index_digest!=self.digest:raise ValueError('属性索引版本不符')
        if limit<1 or not 0<=offset<=len(self.entries):raise ValueError('属性页范围非法')
        end=min(offset+limit,len(self.entries));remaining=self.entries[end]['value'] if end<len(self.entries) else None
        result={'rows':deepcopy(self.entries[offset:end]),'next':end if end<len(self.entries) else None,'complete':end==len(self.entries),'remaining_best':remaining if bound else None,'table_digest':self.table_digest,'index_digest':self.digest,'field':self.field,'direction':self.direction}
        self.events.append({'offset':offset,'rows':end-offset});return result
