import os
from online_users import online_users
from google.cloud import bigtable
from google.cloud.bigtable.row_set import RowSet
from google.auth.credentials import AnonymousCredentials

os.environ['BIGTABLE_EMULATOR_HOST'] = '127.0.0.1:8086'

def read_prefix(project_id='no-project', instance_id='emulator', table_id='test'):
    client = bigtable.Client(project=project_id)#, admin=True)
    
    print(client._emulator_host)
    instance = client.instance('emulator')
    table = instance.table(table_id)
    prefix = "30abe6287f1b3112c6a42d605b84c0f8:following:"
    row_set = RowSet()
    row_set.add_row_range_with_prefix(prefix)
    rows = table.read_rows(row_set=row_set)
    
    return rows 


def main():
    rows = read_prefix()
    matching = []
    total_rows = []

    filtered = list(filter(lambda x: x in online_users, [x.row_key.decode('utf-8').split(':')[2] for x in rows ]))
    print(f'Matched {len(filtered)}')
       
if __name__ == '__main__':
    main()                                         
