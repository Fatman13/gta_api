def test(set):
	if 1 in set:
		set.clear()
		set.add(1)

a = set([1, 2, 3])
print(str(a))

test(a)
print(str(a))