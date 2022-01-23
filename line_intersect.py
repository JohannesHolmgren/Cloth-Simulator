from Point import Point

def is_line_intersect(p1, p2, p3, p4):
    """ p1 and p2 is the end points of line 1 
        and p3 and p4 the end points of line 2 """
    denominator = (p2.x - p1.x) * (p4.y - p3.y) - (p2.y - p1.y) * (p4.x - p3.x)
    numerator1  = (p1.y - p3.y) * (p4.x - p3.x) - (p1.x - p3.x) * (p4.y - p3.y)
    numerator2  = (p1.y - p3.y) * (p2.x - p1.x) - (p1.x - p3.x) * (p2.y - p1.y)

    if denominator == 0:
        return numerator1 == 0 and numerator2 == 0

    r = numerator1 / denominator
    s = numerator2 / denominator

    return (r >= 0 and r <= 1) and (s >= 0 and s <= 1)