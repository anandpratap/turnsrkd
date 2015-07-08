all:
	f2py -c fortutils.f90 -m fortutils
clean:
	rm *.so
