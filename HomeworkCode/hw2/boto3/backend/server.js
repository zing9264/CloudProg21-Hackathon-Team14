var AWS = require('aws-sdk'),
    http = require('http'),
    winston = require('winston');

AWS.config.update({
    region: "us-east-1",
});

var logfile = 'server.log';

var logger = new winston.Logger({
    transports: [ 
        new winston.transports.File({ filename: logfile})
    ]
});

var sns = new AWS.SNS({
    apiVersion: '2010-03-31',
    region: 'us-east-1'
});

http.createServer(function(req,res){

    req.on('data',function(data){
        try{
            var hash = JSON.parse(data.toString());
        }catch(e){
            returnResponse(res,400,logger,'Invalid json: ' + data.toString());
        }
        if(!hash.name){
            returnResponse(res,400,logger,'Invalid name: ' + JSON.parse(hash));
        }
        if(!hash.email){
            returnResponse(res,400,logger,'Invalid email: ' + JSON.parse(hash));
        }
        if (!hash.gender) {
            returnResponse(res,400,logger,'Invalid gender: ' + JSON.parse(hash));
        }
        var gender=''
        if (hash.gender == 'F') {
            gender='Ms.'
        } else if (hash.gender == 'M')  {
            gender='Mr.'
        }
        var memberships = [];
        var docClient = new AWS.DynamoDB.DocumentClient({region: 'us-east-1'});
        var DDBparams = {
            TableName: "HW2table",
            ProjectionExpression: "#name",
            ExpressionAttributeNames: {
                "#name": "name",
            },
        };

        docClient.scan(DDBparams, onScan);

        function onScan(err, data) {
            if (err) {
                console.error("Unable to scan the table. Error JSON:", JSON.stringify(err, null, 2));
                returnResponse(res,400,logger,"Unable to scan the table. Error JSON:", JSON.stringify(err, null, 2)) ;

            } else {
                // print all the movies
                console.log("Scan succeeded.");
                data.Items.forEach(function(user) {
                    console.log(user);
                    console.log(user.name);
                    memberships.push(user.name);
                    console.log(memberships);

                });

                // continue scanning if we have more movies, because
                // scan can retrieve a maximum of 1MB of data
                if (typeof data.LastEvaluatedKey != "undefined") {
                    console.log("Scanning for more...");
                    params.ExclusiveStartKey = data.LastEvaluatedKey;
                    docClient.scan(params, onScan);
                }
                var params = {
                    Message: 'Let’s welcome our new member ['+gender+']['+hash.name +']. His contact email is ['+ hash.email +']. We now have the following members in the club: '+ memberships.toString() +' .', /* required */
                    TopicArn: 'arn:aws:sns:us-east-1:781030094409:club'
                };
                
                // Create promise and SNS service object
                sns.publish(params, function (err, data) {
                    if (err) {
                        console.error(err, err.stack);
                        returnResponse(res,400,logger,"publish SNS "+ params.TopicArn +" error") ;
                    }
                    if (data) {
                        console.log(`Message ${params.Message} sent to the topic ${params.TopicArn}`);
                        console.log("MessageID is " + data.MessageId);
                        returnResponse(res,200,logger,"MessageID is " + data.MessageId) ;
                    }
                });
            }
        }
    });
}).listen(process.env.PORT || 3000);

function returnResponse(httpResponse, status, logger, message){

    if(status === 200){
        logger.info(message);
    }else{
        logger.error(message);
    }

    httpResponse.writeHead(status);
    httpResponse.write(message, 
    	function(err){httpResponse.end();});
}
