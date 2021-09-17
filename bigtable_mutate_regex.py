import os
from codetiming import Timer
from online_users import online_users
from google.cloud import bigtable
from google.cloud import happybase
from google.cloud.bigtable.row_set import RowSet
from google.cloud.bigtable.row_filters import RowKeyRegexFilter, RowFilterChain, ColumnRangeFilter
from google.auth.credentials import AnonymousCredentials


os.environ['BIGTABLE_EMULATOR_HOST'] = '127.0.0.1:8086'

@Timer(text="delete_online took {:.2f} seconds")
def delete_online(streamer, project_id='no-project', instance_id='emulator', table_id='test'):
    client = bigtable.Client(project=project_id)#, admin=True)
    instance = client.instance('emulator')
    table = instance.table(table_id)
    row_set = RowSet()
    filter = RowFilterChain(
        filters= [ 
            RowKeyRegexFilter(f"\C*:following:{streamer}"),
            ColumnRangeFilter("something", b"online", b"online")
        ]
    )
    rows = table.read_rows(row_set=row_set, filter_= filter )
    for read_row in rows:
        row = table.row(read_row.row_key)
        print('deleting ' + row.row_key.decode('utf-8'))
        row.delete_cell('something', 'online')
        row.set_cell('something', 'offline', '' )
        row.commit()


@Timer(text="delete_online_happy took {:.2f} seconds")
def delete_online_happy(streamer, project_id='no-project', instance_id='emulator', table_id='test'):
    client = bigtable.Client(project=project_id, admin=True)
    instance = client.instance(instance_id)
    connection = happybase.Connection(instance=instance)
    table = happybase.Table(table_id, connection)
    filter = RowFilterChain(
        filters= [ 
            RowKeyRegexFilter(f"\C*:following:{streamer}"),
            ColumnRangeFilter("something", b"online", b"online")
        ]
    )
    with happybase.Batch(table=table, transaction=True) as batch:
        for key, row in table.scan(filter=filter):
            batch.delete(row=key, columns=[b'something:online'])
            batch.put(row=key, data={b'something:offline' : b''})
            print('toggling offline for ' + key.decode('utf-8') + ' in batch')


@Timer(text="set_online_happy took {:.2f} seconds")
def set_online_happy(streamer, project_id='no-project', instance_id='emulator', table_id='test'):
    client = bigtable.Client(project=project_id, admin=True)
    instance = client.instance(instance_id)
    connection = happybase.Connection(instance=instance)
    table = happybase.Table(table_id, connection)
    filter = RowFilterChain(
        filters= [ 
            RowKeyRegexFilter(f"\C*:following:{streamer}"),
            ColumnRangeFilter("something", b"offline", b"offline")
        ]
    )
    with happybase.Batch(table=table, transaction=True) as batch:
        for key, row in table.scan(filter=filter):
            batch.put(row=key, data= { b'something:online' : b''})
            batch.delete(row=key, columns=[b'something:offline'])
            print('toggling online for ' + key.decode('utf-8') + ' to batch')

@Timer(text="get_online_for_viewer took {:.2f} seconds")
def get_online_for_viewer(viewer, project_id='no-project', instance_id='emulator', table_id='test'):
    client = bigtable.Client(project=project_id)#, admin=True)
    instance = client.instance('emulator')
    table = instance.table(table_id)
    row_set = RowSet()
    prefix = f"{viewer}:following:"
    row_set = RowSet()
    row_set.add_row_range_with_prefix(prefix)
    filter = ColumnRangeFilter("something", b"online", b"online")
    rows = table.read_rows(row_set=row_set, filter_= filter )
    online_users = [ row.row_key.decode('utf-8') for row in rows ]
    print(f'Number of users online for viewer {viewer}: {len(online_users)}')


def main():
    streamer = "d9ab6db92afd6b45060ad3391abcb433"
    viewer = "96957e0c81f921b7e9a36008652b11ad"
    delete_online(streamer=streamer)
    delete_online_happy(streamer=streamer)
    set_online_happy(streamer=streamer)
    get_online_for_viewer(viewer=viewer)
       
if __name__ == '__main__':
    main()                                         
