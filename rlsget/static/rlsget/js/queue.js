var app = angular.module('rlscloud.rlsget.queue', ['rlscloud']);

app.filter('iconClass', function(){
    var states = {
        0: 'clock-o',
        1: 'download',
        2: 'check',
        3: 'exclamation',
        4: 'refresh'
    };

    return function(stateCode){
        return states[stateCode];
    }
});

app.filter('colorClass', function(){
    var states = {
        0: '',
        1: 'bg-info',
        2: 'bg-success',
        3: 'bg-warning',
        4: 'bg-info'
    };

    return function(stateCode){
        return states[stateCode]
    }
});


app.filter('stateString', ['options', function(options){
    return function(stateCode){
        return options.states[stateCode];
    }
}]);

app.controller('QueueList', ['$http', '$scope', '$interval', 'urls', 'options', function($http, $scope, $interval, urls, options){
    var self = this;

    var QUEUED = 0;
    var DOWNLOADING = 1;
    var FINISHED = 2;
    var ERROR = 3;

    var queueApi = urls.queue_api;

    // Queue listing -----------------------------------------------------------
    var apiQuery = function(){
        $http.get(queueApi)
        .success(function(reply){
            angular.forEach(reply, function(v){
                switch(v.state){
                    case(DOWNLOADING):
                        v.$progress = (v.downloaded / v.total) * 100;
                        break;
                    case(FINISHED):
                        v.$progress = 100;
                        break;
                    case(QUEUED):
                    case(ERROR):
                        v.$progress = 0;
                        break;
                }
            });
            $scope.tasks = reply;
        })
        .error(function(){
            console.log('e', arguments);
        });
    };

    apiQuery();
    var poller = $interval(apiQuery, 1000);

    // Enqueueing URL ----------------------------------------------------------
    $scope.url = '';

    self.enqueueTask = function(){
        $http.post(queueApi, {url: $scope.url})
        .success(function(){
            $scope.url = '';
            apiQuery();
        })
        .error(function(){
            console.log('e', arguments);
        })
    };

    // "Details" row -----------------------------------------------------------
    var openDetails = new Set();

    self.isDetailsOpen = function(task){
        return openDetails.has(task.id);
    } ;

    self.toggleDetails = function(task){
        if(self.isDetailsOpen(task)){
            openDetails.delete(task.id)
        }
        else {
            openDetails.add(task.id);
        }
    }
}]);