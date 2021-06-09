from azure.cosmos import CosmosClient
from flask import Flask, render_template, request, redirect
from flask import request
import os

app = Flask(__name__)

# Initialize the Cosmos client
endpoint = os.environ["endpoint"]
key = os.environ["key"]

# <create_cosmos_client>
client = CosmosClient(endpoint, key)
# </create_cosmos_client>

database_name = 'CarLocations'
database = client.get_database_client(database_name)

container_name = 'Plates'
container = database.get_container_client(container_name)


@app.route('/cosmos-test')
def test():
    query = "SELECT * FROM c"

    items = list(container.query_items(
        query=query,
        enable_cross_partition_query=True
    ))

    print(items)

    request_charge = container.client_connection.last_response_headers['x-ms-request-charge']

    res = 'Query returned {0} items. Operation consumed {1} request units'.format(len(items), request_charge)
    return res


@app.route('/')
def form():
    return render_template('form.html')


@app.route('/data/', methods=['POST', 'GET'])
def select():
    if request.method == 'GET':
        return f"The URL /data is accessed directly. Try going to '/' to submit form"
    if request.method == 'POST':
        result = request.form
        print("result: ", result)
        plate = result['plate']
        print("plate: ", plate)
        query = "SELECT * FROM c WHERE ARRAY_CONTAINS(c.plates, \"" + plate + "\")"

        print("query: ", query)

        items = list(container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))

        print("items: ", items)
        res = []
        img = None
        for row in items:
            res.append([row['camera_id'], row['time'], row['plates']])
            img = row['img']

        print(res)

        return render_template('select.html', result=res, img_data=img)



if __name__ == '__main__':
    app.run()
