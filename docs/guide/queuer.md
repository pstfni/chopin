# 🔮 Queuer

You cannot shuffle through songs in your queue. It is very frustating !

With the `queuer ` entrypoint you can create a playlist from your queue, and do whatever you please with it!

```shell
queuer
```

!!! warning "Spotify API limitation"
    Queues are hard to retrieve from the Spotify API. For this reason, be aware that :
        - You must be _playing_ from a device for this entrypoint to work.
        - The entrypoint will retrieve up to 20 songs from your queue, but not more.

