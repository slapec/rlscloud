var app = angular.module('rlscloud', []);

app.config(['$httpProvider', '$interpolateProvider', function($httpProvider, $interpolateProvider){
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';

    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');
}]);

app.filter('percentage', ['$filter', function ($filter) {
    return function (input, decimals) {
        if(decimals === undefined){
            decimals = 2;
        }
        return $filter('number')(input, decimals) + '%';
    };
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
