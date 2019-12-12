from flask import Flask,request,jsonify
from flask_cors import CORS
import requests
from opentracing.ext import tags
from opentracing.propagation import Format
import logging
from jaeger_client import Config

app = Flask(__name__)
CORS(app)

def init_tracer(service):
    logging.getLogger('').handlers = []
    logging.basicConfig(format='%(message)s', level=logging.DEBUG)

    config = Config(
        config={
            'sampler': {
                'type': 'const',
                'param': 1,
            },
            'local_agent': {
                'reporting_host': 'jaeger',
                'reporting_port': 6831
            },
            'logging': True,
        },
        service_name=service,
    )

    # this call also sets opentracing.tracer
    return config.initialize_tracer()

tracer = init_tracer('CallerService') 

@app.route("/",methods=['POST'])
def caller():
    span = tracer.start_span("Caller")
    payload = request.get_json()
    sqrurl = 'http://sqrapp:5020/'
    # trace_id
    # span.set_tag('Trace_id', span.context.trace_id)
    print('-----------span context---------')
    print(span.context)
    span.set_tag(tags.HTTP_METHOD, 'POST')
    span.set_tag(tags.SPAN_KIND, tags.SPAN_KIND_RPC_CLIENT)
    span.set_tag(tags.HTTP_URL, sqrurl)
    headers = {'Content-Type': 'application/json'}
    tracer.inject(span, Format.HTTP_HEADERS, headers)
    # print("headers------------",headers)
    sqrres = requests.post(sqrurl,json=payload,headers=headers)
    sqrdata = sqrres.json()
    sqrnum1 = int(sqrdata['num1'])
    sqrnum2 = int(sqrdata['num2'])

    cubeurl = 'http://cubeapp:5030/'
    span.set_tag(tags.HTTP_URL, cubeurl)
    # headers = {'Content-Type': 'application/json'}
    # tracer.inject(span, Format.HTTP_HEADERS, headers)
    cuberes = requests.post(cubeurl,json=payload,headers=headers)
    cubedata = cuberes.json()
    cubenum1 = int(cubedata['num1'])
    cubenum2 = int(cubedata['num2'])

    
    finalpayload = {
        "num1" : sqrnum1,
        "num2" : sqrnum2,
        "num3" : cubenum1,
        "num4" : cubenum2
    }

    addurl = 'http://addapp:5040/'
    span.set_tag(tags.HTTP_URL, addurl)
    # headers = {'Content-Type': 'application/json'}
    # tracer.inject(span, Format.HTTP_HEADERS, headers)
    addres = requests.post(addurl,json=finalpayload,headers=headers)
    add_data = addres.json()
    addresult = add_data['result']

    span.finish()
    return jsonify(sqrnum1=sqrnum1,
    sqrnum2=sqrnum2, cubenum1=cubenum1, 
    cubenum2=cubenum2, theresult=addresult)

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5010,debug=True)


