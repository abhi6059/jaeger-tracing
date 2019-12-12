from flask import Flask,request,jsonify
from flask_cors import CORS
import math
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

tracer = init_tracer('AddedNum') 

@app.route("/",methods=['POST'])
def add():
    parentspan = tracer.extract(Format.HTTP_HEADERS, request.headers)
    span_tags = {tags.SPAN_KIND: tags.SPAN_KIND_RPC_SERVER}
    span = tracer.start_span("Add", child_of=parentspan,tags=span_tags)
    data = request.get_json()
    num1 = int(data['num1'])
    num2 = int(data['num2'])
    num3 = int(data['num3'])
    num4 = int(data['num4'])
    span.log_kv({'event': 'adding', 'num1': num1, 'num2': num2, 'num3': num3, 'num4': num4})
    res = num1+num2+num3+num4
    span.finish()
    return jsonify(result=res)

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5040,debug=True)
