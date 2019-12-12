const express = require('express');
const bodyParser = require('body-parser');
const initJaegerTracer = require("jaeger-client").initTracer;
const { Tags, FORMAT_HTTP_HEADERS } = require('opentracing');

const app = express();
const port = 9003;

app.use(bodyParser.json()); // support json encoded bodies
app.use(bodyParser.urlencoded({ extended: true })); // support encoded bodies

function initTracer(serviceName) {
    const config = {
      serviceName: serviceName,
      sampler: {
        type: "const",
        param: 1,
      },
      reporter: {
        agentHost: 'jaeger',
        agentPort: 6832,
        logSpans: true,
      },
    };
    const options = {
      logger: {
        info(msg) {
          console.log("INFO ", msg);
        },
        error(msg) {
          console.log("ERROR", msg);
        },
      },
    };
    return initJaegerTracer(config, options);
}

const tracer = initTracer("adder");

app.post("/",(req,res)=>{
    const parentSpan = tracer.extract(FORMAT_HTTP_HEADERS, req.headers)
    const span = tracer.startSpan("add",{
      childOf: parentSpan,
      tags: {[Tags.SPAN_KIND]: Tags.SPAN_KIND_RPC_SERVER}});
    var num1 = req.body.num1;
    var num2 = req.body.num2;
    var num3 = req.body.num3;
    var num4 = req.body.num4;
    var result = num1+num2+num3+num4;
    span.log({event: "addition", "num1": num1, "num2": num2, "num3": num3, "num4": num4});
    span.finish();
    res.send(JSON.stringify({result : result}));
})

app.listen(port, ()=>{
    console.log('Listening port 9003');
})
