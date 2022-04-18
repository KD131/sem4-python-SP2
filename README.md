# SP 2 - Rotten Tomatoes
*by Team Tons (Oliver Stæhr, Magnus Granno, Aleksander Rolander)*

Datasæt:
- https://www.rottentomatoes.com/top/bestofrt/?year=2020
- https://www.rottentomatoes.com/top/bestofrt/?year=2010
- https://www.rottentomatoes.com/top/bestofrt/?year=1990

1. Scrape navn, genre, runtime, tomatometer score og audience score på filmene fra årstallet 2020 og 1990
	- Hvis en film har flere genre så tilhører den alle de forskellige genre grupper

2. Vis den gennemsnitlige audience score for hver genre i 2020 og 2010, i den samme barchart

3. Find den genre hvor der er størst forskel fra audience score og tomatometer score i 2010
	- har det ændret sig i 2020?
	- hvis ja
		- vis en barchart af de forskellige genre
	
4. Hvad er den gennemsnitlige runtime for genren 'drama' i 2010 og 2020?

# Status

1-2 + 4 solved.

To run it, just execute the python file like so: `python rotten_tomatoes.py`

If the CSV files `movies_year.csv` are not present in the folder, it will attempt to scrape the data and save it to CSV. You can also force this behaviour by passing `refresh=True` to the `get_movies()` function.

The script will show a plot of the average audience rating of each genre for 2010 and 2020. After closing the plot window, it will then print the average runtime of dramas for 2010 and 2020.
