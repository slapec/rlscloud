var app = angular.module('rlscloud.rlsget.queue', ['rlscloud']);

app.filter('iconClass', function(){
    var states = {
        0: 'clock-o',
        1: 'download',
        2: 'refresh',
        3: 'check',
        4: 'exclamation'
    };

    return function(stateCode){
        return states[stateCode];
    }
});

app.filter('colorClass', function(){
    var states = {
        0: '',
        1: 'bg-info',
        2: 'bg-info',
        3: 'bg-success',
        4: 'bg-warning'
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
    var PROCESSING = 2;
    var FINISHED = 3;
    var ERROR = 4;

    var CANCELABLE_STATES = new Set([QUEUED, DOWNLOADING, PROCESSING]);
    var ARCHIVABLE_STATES = new Set([FINISHED, ERROR]);

    var queueApi = urls.queue_api;

    // Queue listing -----------------------------------------------------------
    var apiQuery = function(){
        $http.get(queueApi)
        .success(function(reply){
            angular.forEach(reply, function(v){
                switch(v.state){
                    case(PROCESSING):
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

                if(!v.started_at){
                    v.started_at = options.i18n.na;
                    v.$runtime = options.i18n.na;
                    v.$wait = new Date() - new Date(v.created_at);
                }
                else {
                    v.$runtime = new Date() - new Date(v.started_at);
                    v.$wait = new Date(v.started_at) - new Date(v.created_at);
                }

                if(!v.finished_at){
                    v.finished_at = options.i18n.na;
                }
                else {
                    v.$runtime = new Date(v.finished_at) - new Date(v.started_at);
                }
            });
            $scope.tasks = reply;
        })
        .error(function(){
            console.log('e', arguments);
        });
    };

    apiQuery();
    var poller = $interval(apiQuery, 3000);

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

    self.archive = function(task){
        $http.patch(queueApi, {id: task.id})
            .success(function(){
                apiQuery();
            })
            .error(function(){
                console.log(2, arguments);
            });
    };

    self.cancel = function(task){
       $http.delete(queueApi, {id: task.id})
           .success(function(){
               apiQuery();
           })
           .error(function(){
               console.log(2, arguments);
           });
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
    };

    self.isArchivable = function(task){
        return ARCHIVABLE_STATES.has(task.state);
    };

    self.isCancelable = function(task){
        return CANCELABLE_STATES.has(task.state)
    };

    self.hasError = function(task){
        return task.state === ERROR;
    }
}]);