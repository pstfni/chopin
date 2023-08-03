# 📝 Describe

Store and get statistics about your playlist with the `describe` entrypoint.

You can display statistics of a playlist :

<div class="termy">

```console
$ describe --name "rock" 

📝 Describing ...
<font color="#6ed47d">
------ Playlist rock ------
	254 tracks
	151 artists
	average features
	    acousticness=0.19 
	    danceability=0.646 
	    energy=0.654 
	    instrumentalness=0.097 
	    liveness=0.167 
	    loudness=-7.509 
	    speechiness=0.051 
	    valence=0.589 
	    tempo=123.178
	    mode=0.669 
	    key=5.24
</font>
```
</div>

If you don't specify a name, all your playlists will be saved

<div class="termy">

```console
$ describe
```
</div>

If you specify an output directory, the entrypoint will dump all the tracks data in a readable JSON. 

<div class="termy">

```console
$ describer --output data/ 

📝 Describing . . .
Wrote playlist pop in data/pop.json
Wrote playlist rock in data/rock.json
Wrote playlist electro in data/electro.json
```
</div>