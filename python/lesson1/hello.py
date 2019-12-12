import sys
import opentracing
import logging
from jaeger_client import Config
import time

# tracer = opentracing.tracer

# an instance of a real tracer,such as Jaege
def init_tracer(service):
    logging.getLogger('').handlers = []
    logging.basicConfig(format='%(message)s', level=logging.DEBUG)

    config = Config(
        config={
            'sampler': {
                'type': 'const',
                'param': 1,
            },
            'logging': True,
        },
        service_name=service,
    )

    # this call also sets opentracing.tracer
    return config.initialize_tracer()


# def say_hello(hello_to):
#     span = tracer.start_span('say-hello')
#     hello_str = 'Hello, %s!' % hello_to
#     print(hello_str)
#     span.finish()

tracer = init_tracer('hello-world')


# def say_hello(hello_to):
#     with tracer.start_span('say-hello') as span:
#         hello_str = 'Hello, %s!' % hello_to
#         print(hello_str)


def say_hello(hello_to):
    span = tracer.start_span('say-hello-operation')
    hello_str = 'Hello, %s!' % hello_to
    print(hello_str)
    span.finish()

assert len(sys.argv) == 2

hello_to = sys.argv[1]
say_hello(hello_to)

time.sleep(2)
tracer.close()

