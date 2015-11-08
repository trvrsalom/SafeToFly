import json
from shapely.geometry import Point, shape
import SocketServer
import urlparse
from BaseHTTPServer import BaseHTTPRequestHandler

def checkPos(lat, lon):
    with open('5_mile_airport.json', 'r') as f:
        js = json.load(f)
    point = Point(lon, lat)
    for feature in js['features']:
        polygon = shape(feature['geometry'])
        if polygon.contains(point):
            return json.JSONEncoder().encode({ "safe" : "false"})
    with open('unitedstates.json', 'r') as f:
        js = json.load(f)
    inUS = 0
    for feature in js['features']:
        polygon = shape(feature['geometry'])
        if polygon.contains(point):
            inUS = 1
            break;
    if inUS == 1:
        with open('us_military.json', 'r') as f:
            js = json.load(f)
        for feature in js['features']:
            polygon = shape(feature['geometry'])
            if polygon.contains(point):
                return json.JSONEncoder().encode({ "safe" : "false"})
        with open('us_national_park.json', 'r') as f:
            js = json.load(f)
        for feature in js['features']:
            polygon = shape(feature['geometry'])
            if polygon.contains(point):
                return json.JSONEncoder().encode({ "safe" : "false"})
        return json.JSONEncoder().encode({ "safe" : "true"})
    else:
        return json.JSONEncoder().encode({ "safe" : "caution"})


class ServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path=='/favicon.ico':
            return
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        parsed = urlparse.urlparse(self.path)
        data = urlparse.parse_qs(parsed.query)
        print "Request from: (" + data['lat'][0] + ", " + data['lon'][0] + ")"
        self.wfile.write(checkPos(float(data['lat'][0]), float(data['lon'][0])))

SocketServer.ThreadingTCPServer.allow_reuse_address = True
server = SocketServer.ThreadingTCPServer(("localhost", 8080), ServerHandler)
server.serve_forever()
