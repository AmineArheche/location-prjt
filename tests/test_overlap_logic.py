def is_overlapping(start1, end1, start2, end2):
    return (start1 < end2) and (end1 > start2)

def test_overlap_detection():
    # Cas chevauchement
    assert is_overlapping(10, 20, 15, 25) is True
    # Cas disjoint
    assert is_overlapping(10, 20, 20, 30) is False
    assert is_overlapping(10, 20, 21, 30) is False
