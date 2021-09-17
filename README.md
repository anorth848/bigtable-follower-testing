# Some BigTable testing using the BigTable Emulator   
The purpose of this is to demonstrate and test possible approaches to retrieve records from BigTable related to who a user is following, but only if the followed user is online   
User ids are md5 hashed for more even distribution (and to match the existing data architecture)   

## Row key design    

The row key is `{md5_acct_id}:following:{md5_acct_id}`. The first `md5_acct_id` is the logged in user, and the 2nd will be each user that the logged in user is following.

## Setup

### Configure and launch the bigtable emulator

bash ./setup.sh

### Add some data

#### [add_rows.sh](add_rows.sh)    
Will add data until canceled, starting with the same md5 hash   
Use a different `$1` for each run.. this would represent a unique user   
The "following" id is generated based on the loop #, starting with the same for each run to simulate a streamer having more than one follower

```
bash ./add_rows.sh aiden
added 95c23aa80bdeaee8a3cf6c68e2017885:following:bc3f3efe68b70a07845d363f1cc1b4c3
added 95c23aa80bdeaee8a3cf6c68e2017885:following:1121aa697ff764b742c41255e16825a6
added 95c23aa80bdeaee8a3cf6c68e2017885:following:97dd96d5680e9a0cbdb7a3d43ddaa86e
added 95c23aa80bdeaee8a3cf6c68e2017885:following:4ab987c1f30d3cbfcab3a271c4987152
added 95c23aa80bdeaee8a3cf6c68e2017885:following:d9ab6db92afd6b45060ad3391abcb433
added 95c23aa80bdeaee8a3cf6c68e2017885:following:a79b8ea16ad991c31bb9e873274d8a0b
added 95c23aa80bdeaee8a3cf6c68e2017885:following:f858ca775796efe8052f179dae5224e4

$ bash ./add_rows.sh olivia
added 2889b86cc1978b0e34540b5a626fb70f:following:bc3f3efe68b70a07845d363f1cc1b4c3
added 2889b86cc1978b0e34540b5a626fb70f:following:1121aa697ff764b742c41255e16825a6
added 2889b86cc1978b0e34540b5a626fb70f:following:97dd96d5680e9a0cbdb7a3d43ddaa86e
added 2889b86cc1978b0e34540b5a626fb70f:following:4ab987c1f30d3cbfcab3a271c4987152
added 2889b86cc1978b0e34540b5a626fb70f:following:d9ab6db92afd6b45060ad3391abcb433
added 2889b86cc1978b0e34540b5a626fb70f:following:a79b8ea16ad991c31bb9e873274d8a0b
added 2889b86cc1978b0e34540b5a626fb70f:following:f858ca775796efe8052f179dae5224e4
```

## Testing scripts

Each python script can be run with no arguments, update values as needed, please excuse the hard-coding ;)

### Filtering on the BigTable side    

Here we explore different ways to query and filter in BigTable to see which yields the best performance.   

#### [bigtable_filters.py](bigtable_filters.py)

This generates a RowFilterUnion (logical AND) of RowKeyRegexFilter filters for all users in [online_users.py]()   
It's ugly, and doesn't perform well.. not recommended to ever do this   

#### [bigtable_prefix_column_range.py](bigtable_prefix_column_range.py)    

This is a prefix search with a ColumnRangeFilter, only return rows that contain this specific column

#### [bigtable_rowkeys.py](bigtable_rowkeys.py)

This generates a RowSet of specific rowkeys for all users in [online_users.py]()    
Performs better than RowFilterUnion/RowKeyRegexFilter and matches the existing architecture/approach

#### [bigtable_mutate_regex.py](bigtable_mutate_regex.py)

This is the most complete example. This does a few things.    
1. Demonstrates the same functionality using both  `google.client.bigtable` and `google.client.happybase`   
1. `delete_online(streamer=streamer)`    and `delete_online_happy(streamer=streamer)`   
    * For all followers of a streamer, Removes the column "online" and adds a column "offline" to indicate the streamer has gone offline
1. `set_online_happy(streamer=streamer)`
   * For all followers of a streamer, Removes the column "offline" and adds a column "online" to indicate the streamer has gone online using HappyBase
1. `get_online_for_viewer(viewer=viewer)`
   * Retrieve all streamers for a viewer who are currently online

### Filtering on the Client side

The following scripts pull all records for a viewer's row key prefix and then filter on the client side

#### [client_filter_mp.py](client_filter_mp.py)    
Use multiprocessing to construct the results from a prefix scan, bump up against [online_users.py](online_users.py) to see who is online   
This did not perform well in my testing, but didn't spend much time on it, probably can be optimized

#### [client_filtering.py](client_filtering.py)    
Use a filter on the client side, comparing with [online_users.py](online_users.py) to see who is online
