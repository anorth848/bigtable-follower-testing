import os
from online_users import online_users
from google.cloud import bigtable
from google.cloud.bigtable.row_set import RowSet

os.environ['BIGTABLE_EMULATOR_HOST'] = '127.0.0.1:8086'


def read_rows(project_id='no-project', instance_id='emulator', table_id='test'):
    client = bigtable.Client(project=project_id)#, admin=True)
    instance = client.instance('emulator')
    table = instance.table(table_id)
    prefix = "30abe6287f1b3112c6a42d605b84c0f8:following:"
    row_set = RowSet()
    
    for k in online_users:
        record = f'{prefix}{k}'
        row_set.add_row_key(record.encode('utf-8'))

    rows = table.read_rows(row_set=row_set)
    streamers = [x.row_key.decode('utf-8').split(':')[2] for x in rows ]
    return streamers 


def main():
    streamers = read_rows()
    print(f'Matched {len(streamers)}')
       
if __name__ == '__main__':
    main()                                         
