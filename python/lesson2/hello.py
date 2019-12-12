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

tracer = init_tracer('hello-world')

#different operation under same service but 3 different standalone trace

# def say_hello(hello_to):
#     with tracer.start_span('say-hello') as span:
#         span.set_tag('hello-to', hello_to)
#         hello_str = format_string(span, hello_to)
#         print_hello(span, hello_str)

# def format_string(root_span, hello_to):
#     with tracer.start_span('format') as span:
#         hello_str = 'Hello, %s!' % hello_to
#         span.log_kv({'event': 'string-format', 'value': hello_str})
#         return hello_str

# def print_hello(root_span, hello_str):
#     with tracer.start_span('println') as span:
#         print(hello_str)
#         span.log_kv({'event': 'println'})



#different operation under same service (as child span)
# def say_hello(hello_to):
#     with tracer.start_span('say-hello') as span:
#         span.set_tag('hello-to', hello_to)
#         hello_str = format_string(span, hello_to)
#         print_hello(span, hello_str)

# def format_string(root_span, hello_to):
#     with tracer.start_span('format',child_of=root_span) as span:
#         hello_str = 'Hello, %s!' % hello_to
#         span.log_kv({'event': 'string-format', 'value': hello_str})
#         return hello_str

# def print_hello(root_span, hello_str):
#     with tracer.start_span('println',child_of=root_span) as span:
#         print(hello_str)
#         span.log_kv({'event': 'println'})


#different operation under same service (as child span) without passing span(using start_active_span)
def say_hello(hello_to):
    with tracer.start_active_span('say-hello') as scope:
        scope.span.set_tag('hello-to', hello_to)
        hello_str = format_string(hello_to)
        print_hello(hello_str)

def format_string(hello_to):
    with tracer.start_active_span('format') as scope:
        hello_str = 'Hello, %s!' % hello_to
        scope.span.log_kv({'event': 'string-format', 'value': hello_str})
        return hello_str

def print_hello(hello_str):
    with tracer.start_active_span('println') as scope:
        print(hello_str)
        scope.span.log_kv({'event': 'println'})

assert len(sys.argv) == 2

hello_to = sys.argv[1]
say_hello(hello_to)

time.sleep(2)
tracer.close()
