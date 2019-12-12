//require module
const express = require('express');
const initJaegerTracer = require("jaeger-client").initTracer;
//express initialize
const app = express();

const port = 8000;


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

const tracer = initTracer("hello-world");

app.listen(port,()=>{
    console.log('listen port 8000');
})

//create api
app.get('/', (req,res)=>{
    const span = tracer.startSpan("say-hello");
    span.setTag("Hello to","World");
    span.finish();
    res.send(JSON.stringify({msg : 'Hello World'}));
})