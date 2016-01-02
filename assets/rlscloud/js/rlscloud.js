var app = angular.module('rlscloud', []);

app.config(['$httpProvider', '$interpolateProvider', function($httpProvider, $interpolateProvider){
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';

    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');
}]);

app.filter('percentage', ['$filter', function ($filter) {
    return function (input) {
        if(!input){
            input = 0;
        }

        return $filter('number')(input, 2);
    };
}]);

app.filter('timedelta', function(){
    return function(delta){
        if(typeof delta === 'string'){
            return delta
        }
        else {
            // Slightly modified version of
            // http://stackoverflow.com/a/6313008

            var deltaSeconds = Math.floor(delta / 1000);
            var hours = Math.floor(deltaSeconds / 3600);
            var minutes = Math.floor((deltaSeconds - (hours * 3600)) / 60);
            var seconds = deltaSeconds - (hours * 3600) - (minutes * 60);

            if (hours < 10){
                hours = '0' + hours;
            }
            if (minutes < 10){
                minutes = '0' + minutes;
            }
            if (seconds < 10) {
                seconds = '0' + seconds;
            }
            return hours + ':' + minutes + ':' + seconds;
        }
    }
});

app.filter('speed', ['$filter', function($filter){
    var kbyte = 1024;
    var mbyte = 1024 * kbyte;
    var gbyte = 1024 * mbyte;

    return function(value){
        var speed = 0;
        var prefix = 'B';
        if(value > gbyte){
            speed = $filter('number')(value / gbyte, 2);
            prefix = 'GiB';
        }
        else if(value > mbyte){
            speed = $filter('number')(value / mbyte, 2);
            prefix = 'MiB';
        }
        else if(value > kbyte){
            speed = $filter('number')(value / kbyte, 2);
            prefix = 'KiB';
        }

        return speed + ' ' + prefix + '/s';
    }
}]);

app.factory('options', function(){
    return JSON.parse($('#rlscloud-options').html());
});

app.factory('urls', function(){
    return JSON.parse($('#rlscloud-urls').html());
});

app.run(['options', function(options){
    var activeMenuId = options.active;
    if(activeMenuId !== undefined){
        $('#' + activeMenuId).addClass('active')
    }
}]);
