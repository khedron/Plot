## Background ##

I originally wrote a graphing program in C.
I then rewrote it in C++ and then bolted a Qt GUI onto it.
Now I'm starting over in Python, using the PyQt toolkit for a GUI.

## Mission statement ##

The idea is to allow:

-	any units to be used along the axes, even uneven units like dates.
	(For example, months should be evenly spaced even though they last
	for anything between 28 and 31 days).

-	multiple formats - xls, csv and maybe even sql

-	trendlines & arbitrary functions to be plotted

-	a line editor, where a function will be generated that plots the right line.
	Maybe just a combination of bezier curves.

We'll see how far this gets.
