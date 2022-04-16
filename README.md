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
**Copied from last SP. Edit later.**

1-5 solved. 6 half solved because the map already interactive through using Markers in Folium.

To run it, just execute the python file like so: `python cph_monuments.py`

The script will print various results of the exercises and also create two map files.

You can view the resulting maps by opening `single_monument.html` or `all_monuments.html`.
