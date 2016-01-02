var app = angular.module('rlscloud.rls.details', ['rlscloud']);

app.controller('Details', ['$scope', '$http', function($scope, $http){
    var self = this;

    self.encodeRequest = function(url){
        $http.get(url)
        .success(function(){
            // TODO: Feedback
        })
        .error(function(){
            console.log(2, arguments);
        });
    }
}]);
