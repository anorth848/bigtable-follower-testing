import os
from online_users import online_users
from google.cloud import bigtable
from google.cloud.bigtable.row_set import RowSet
from google.auth.credentials import AnonymousCredentials
from multiprocessing import Pool

os.environ['BIGTABLE_EMULATOR_HOST'] = '127.0.0.1:8086'

def filter_online(streamer):
    match=False
    if streamer in online_users:
        match=True
    return match


def read_prefix(project_id='no-project', instance_id='emulator', table_id='test'):
    client = bigtable.Client(project=project_id)#, admin=True)
    instance = client.instance('emulator')
    table = instance.table(table_id)
    prefix = "96957e0c81f921b7e9a36008652b11ad:following:"
    row_set = RowSet()
    row_set.add_row_range_with_prefix(prefix)
    rows = table.read_rows(row_set=row_set)
    streamers = [row.row_key.decode('utf-8').split(':')[2] for row in rows]
    return streamers


def main():
    streamers = read_prefix()
    pool=Pool(4)
    filtered = [c for c, matched in zip(streamers, pool.map(filter_online, streamers)) if matched]
    print(f'Matched {len(filtered)}')

       
if __name__ == '__main__':
    main()                                         
