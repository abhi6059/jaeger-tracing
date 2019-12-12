from flask import Flask,jsonify
from flask_cors import CORS
# from opentracing.ext import tags
# from opentracing.propagation import Format
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

tracer = init_tracer('hello-world-api')

@app.route("/")
def hello():
    with tracer.start_active_span('hello'):
        return jsonify(msg = "hello world!")

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000,debug=True)
