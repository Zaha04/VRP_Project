
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import gmaps
import urllib
import json
import googlemaps
import pandas as pd
import IPython
from ipywidgets.embed import embed_minimal_html
import ipywidgets
API_KEY = ''
gmaps.configure(api_key=API_KEY)


po=[]
data=['Brasov','Codlea','Sacele','Rasnov']
e=data
request_1 = 'https://maps.googleapis.com/maps/api/geocode/json?address='
test=[]
shipments = {}

fig = gmaps.figure()
for j in e:
    test.append(json.loads(urllib.request.urlopen((request_1 + j + '&key=' + API_KEY).replace(' ', '+')).read()))
    # jsonRes = urllib.request.urlopen((request_1 + j + '&key=' + API_KEY).replace(' ', '+')).read()
    # request_2 = (request_1 + j + '&key=' + API_KEY).replace(' ', '+')
final=[]
for i in range(len(test)):
    city = {}
    coordonate = []
    lat=test[i]['results'][0]['geometry']['location']['lat']
    lng=test[i]['results'][0]['geometry']['location']['lng']
    key = test[i]['results'][0]['address_components'][0]['long_name']
    coordonate.append(lat)
    coordonate.append(lng)
    city['city']=key
    city['location']=float(lat),float(lng)
    print(city['location'])
    final.append(city)

print(final)
po.append(final)
print(po)
depot = {
'location':(test[0]['results'][0]['geometry']['location']['lat'], test[0]['results'][0]['geometry']['location']['lng'])
}


depot_layer = gmaps.symbol_layer(
    [depot['location']], hover_text='Depot', info_box_content='Depot',
    fill_color='white', stroke_color='red', scale=8
)

depot_layer = gmaps.symbol_layer(
    [depot['location']], hover_text='Depot', info_box_content='Depot',
    fill_color='white', stroke_color='red', scale=8
    )
num_vehicles = 1

colors = ['blue', 'red', 'green', '#800080', '#000080', '#008080']








#for i in range(len(city[i]['location'])):
shipment_locations = [final[i]['location'] for i in range(1,len(final))]

print(shipment_locations)
shipments_layer = gmaps.symbol_layer(
    shipment_locations, hover_text=[final[i]['city'] for i in range(1,len(final))],info_box_content=[final[i]['city'] for i in range(1,len(final))],
    fill_color='white', stroke_color='black', scale=4
)
fig.add_layer(depot_layer)
fig.add_layer(shipments_layer)
# fig.add_layer(depot_layer)
# fig.add_layer(shipments_layer)
def build_distance_matrix(depot, final, measure='distance'):

    gmaps_services = googlemaps.Client(key=API_KEY)
    origins = destinations = [item['location'] for item in [depot] + final]
    dm_response = gmaps_services.distance_matrix(origins=origins, destinations=destinations)
    dm_rows = [row['elements'] for row in dm_response['rows']]
    distance_matrix = [[item[measure]['value'] for item in dm_row] for dm_row in dm_rows]
    return distance_matrix


try:
    objective = 'distance'  # distance or duration
    # Distance Matrix API takes a max 100 elements = (origins x destinations), limit to 10 x 10

    distance_matrix = build_distance_matrix(depot, final, objective)
    print(distance_matrix)



except:
    print('Something went wrong building distance matrix.')



"""Stores the data for the problem."""
data = {}
data['distance_matrix'] = distance_matrix
data['num_vehicles'] = num_vehicles
data['depot'] = 0


def print_solution(manager, routing, solution):
    """Prints solution on console."""
    print('Objective: {} meters'.format(solution.ObjectiveValue()))
    index = routing.Start(0)
    plan_output = 'Route for vehicle 0:\n'
    route_distance = 0
    while not routing.IsEnd(index):
        plan_output += ' {} ->'.format(manager.IndexToNode(index))
        previous_index = index
        index = solution.Value(routing.NextVar(index))
        route_distance += routing.GetArcCostForVehicle(previous_index, index, 0)
    plan_output += ' {}\n'.format(manager.IndexToNode(index))
    print(plan_output)
    plan_output += 'Route distance: {}meters\n'.format(route_distance)




    """Entry point of the program."""
    # Instantiate the data problem.


# Create the routing index manager.
manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                           data['num_vehicles'], data['depot'])

# Create Routing Model.
routing = pywrapcp.RoutingModel(manager)





def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

transit_callback_index = routing.RegisterTransitCallback(distance_callback)

# Define cost of each arc.
routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

# Setting first solution heuristic.
search_parameters = pywrapcp.DefaultRoutingSearchParameters()
search_parameters.first_solution_strategy = (
routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

# Solve the problem.
solution = routing.SolveWithParameters(search_parameters)


# Print solution on console.

routes = {}
for vehicle_id in range(num_vehicles):
        routes[vehicle_id] = []
        index = routing.Start(vehicle_id)
        while not routing.IsEnd(index):
            routes[vehicle_id].append(manager.IndexToNode(index))
            previous_index = index
            index = solution.Value(routing.NextVar(index))
        routes[vehicle_id].append(manager.IndexToNode(index))


print_solution(manager, routing, solution)

print(routes)


for vehicle_id in routes:
        waypoints = []

        # skip depot (occupies first and last index)
        for final_index in routes[vehicle_id][1:-1]:
            waypoints.append(final[final_index - 1]['location'])
        print(waypoints)

route_layer = gmaps.directions_layer(
                depot['location'], waypoints[-1], waypoints=waypoints[0:-1], show_markers=True,
                stroke_color=colors[1], stroke_weight=5, stroke_opacity=0.5)
fig.add_layer(route_layer)




return_layer = gmaps.directions_layer(
                waypoints[-1], depot['location'], show_markers=False,
                stroke_color=colors[2], stroke_weight=5, stroke_opacity=0.5)
fig.add_layer(return_layer)



fig


        #     return fig
    #
    # a=map_solution(depot, final, routes)
    #
    # print(a)






embed_minimal_html('export.html', views=[fig])








