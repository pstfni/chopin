# 📝 Describer

Backup and get statistics about your playlist with the `describer` entrypoint.

You can display statistics of a playlist :

```shell
describer --name "rock"
```

If you don't specify a name, all your playlists will be analyzed

```shell
describer
```

If you specify an output directory, the entrypoint will dump all the tracks data in a readable JSON. 

```shell
describer --output output_directory/
```

todo: display results here