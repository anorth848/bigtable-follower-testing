import os
from google.cloud import bigtable
from google.cloud.bigtable.row_set import RowSet
from google.cloud.bigtable.row_filters import ColumnRangeFilter

os.environ['BIGTABLE_EMULATOR_HOST'] = '127.0.0.1:8086'


def read_prefix(project_id='no-project', instance_id='emulator', table_id='test'):
    client = bigtable.Client(project=project_id)#, admin=True)
    instance = client.instance('emulator')
    table = instance.table(table_id)
    prefix = "96957e0c81f921b7e9a36008652b11ad:following:"
    row_set = RowSet()
    row_set.add_row_range_with_prefix(prefix)
    filter = ColumnRangeFilter("something", b"online", b"online")
    rows = table.read_rows(row_set=row_set, filter_= filter )
    streamers = [x.row_key.decode('utf-8').split(':')[2] for x in rows ]
    return streamers 


def main():
    streamers = read_prefix()
    print(f'Matched {len(streamers)}')
       
if __name__ == '__main__':
    main()                                         
