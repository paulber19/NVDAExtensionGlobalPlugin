def nbBits(n):
	if n== 0:
		return 0
	i = 0
	while n:
		i += 1
		n = int(n/2)
		print ("n: %s"%n)
	return i-1
	