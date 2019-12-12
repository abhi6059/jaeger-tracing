const express = require('express');
const bodyParser = require('body-parser');
const axios = require('axios');
const initJaegerTracer = require("jaeger-client").initTracer;
const { Tags, FORMAT_HTTP_HEADERS } = require('opentracing');

const app = express();
const port = 9000;
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

const tracer = initTracer("caller");

app.post("/", (req,res)=>{
  const span = tracer.startSpan("call");
  var num1 = req.body.num1;
  var num2 = req.body.num2;
  const sqrurl = 'http://sqrnode:9001';
  const cubeurl = 'http://cubenode:9002';
  const addurl = 'http://addnode:9003';
  const headers = {'Content-Type': 'application/json'};
  span.setTag(Tags.HTTP_METHOD, 'POST');
  span.setTag(Tags.SPAN_KIND, Tags.SPAN_KIND_RPC_CLIENT);
  span.setTag(Tags.HTTP_URL, sqrurl);
  tracer.inject(span, FORMAT_HTTP_HEADERS, headers);
  axios.post(sqrurl, {
      num1 : num1,
      num2 : num2
    },
    {
      headers : headers
    })
    .then(function (response) {
      sqrnum1 = response.data.sqrnum1;
      sqrnum2 = response.data.sqrnum2;
      console.log(response.data);

      span.setTag(Tags.HTTP_URL, cubeurl);
      axios.post(cubeurl, {
        num1 : num1,
        num2 : num2,
      },
      {
        headers : headers
      })
      .then (function(response1) {
        cubenum1 = response1.data.cubenum1;
        cubenum2 = response1.data.cubenum2;
        console.log(response1.data);
        
        span.setTag(Tags.HTTP_URL, addurl);
        axios.post(addurl, {
          num1 : sqrnum1,
          num2 : sqrnum2,
          num3 : cubenum1,
          num4 : cubenum2
        },
        {
          headers : headers
        })
        .then (function(response2){
          result = response2.data.result;
          console.log(response2.data);

          span.finish();
          res.send(JSON.stringify({sqrnum1:sqrnum1,sqrnum2:sqrnum2,cubenum1:cubenum1,
          cubenum2:cubenum2,result:result}));
        })
        .catch(function(error2){
          console.log(error2);
        })
      })
      .catch(function (error1){
        console.log(error1);
      })
    })
    .catch(function (error) {
      console.log(error);
    });
})


app.listen(port , ()=>{
    console.log("Listening to 9000");
})

// app.post("/sqr", (req,res)=>{
//   var num1 = req.body.num1;
//   var num2 = req.body.num2;

//   axios.post('http://localhost:9001', {
//       num1 : num1,
//       num2 : num2
//     })
//     .then(function (response) {
//       sqrnum1 = response.data.sqrnum1;
//       sqrnum2 = response.data.sqrnum2;
//       console.log(response.data);
//       res.send(JSON.stringify({sqrnum1: sqrnum1, sqrnum2: sqrnum2}));
//     })
//     .catch(function (error) {
//       console.log(error);
//     });
// })

// app.post("/cube", (req,res)=>{
//     var num1 = req.body.num1;
//     var num2 = req.body.num2;

//     axios.post('http://localhost:9002', {
//         num1 : num1,
//         num2 : num2
//       })
//       .then(function (response) {
//         cubenum1 = response.data.cubenum1;
//         cubenum2 = response.data.cubenum2;
//         console.log(response.data);
//         res.send(JSON.stringify({cubenum1: cubenum1, cubenum2: cubenum2}));
//       })
//       .catch(function (error) {
//         console.log(error);
//       });
// })

// app.post("/add", (req,res)=>{
//     var num1 = req.body.num1;
//     var num2 = req.body.num2;
//     var num3 = req.body.num3;
//     var num4 = req.body.num4;

//     axios.post('http://localhost:9003', {
//         num1 : num1,
//         num2 : num2,
//         num3 : num3,
//         num4 : num4
//       })
//       .then(function (response) {
//         var addres = response.data.result;
//         console.log(response.data.result);
//         res.send(JSON.stringify({result : addres}));
//       })
//       .catch(function (error) {
//         console.log(error);
//       });
// })




