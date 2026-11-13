"""组合成本的精确评分与物理顺序。"""
def score(row,weights):
    if not weights or any(type(w) is not int or w==0 for w in weights.values()):raise ValueError('评分权重非法')
    total=0
    for field,weight in weights.items():
        value=row.get(field)
        if value is None:return None
        if type(value) is not int or not -(2**63)<=value<2**63:raise ValueError('评分属性类型非法')
        total+=weight*value
    return total

def physical_key(row,weights):
    value=score(row,weights)
    if value is None:raise ValueError('记录无完整评分')
    return value,row['row_id'].encode('utf-8')
