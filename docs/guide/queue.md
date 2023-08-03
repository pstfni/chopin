# 🔮 Queue

You cannot shuffle through songs in your queue, so let's create a playlist to do so !

The `queue` entrypoint create a playlist from the songs in your queue.

<div class="termy">

```console
$ queue 

🔮 Queuing . . .
Playlist '🔮 Queued Mix' successfully created.
```
</div>


!!! warning "Spotify API limitation"
    Queues are hard to retrieve from the Spotify API. For this reason, be aware that :
        - You must be _playing_ from a device for this entrypoint to work.
        - The entrypoint will retrieve up to 20 songs from your queue, but not more.

