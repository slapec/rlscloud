var app = angular.module('rlscloud.rls.details', ['rlscloud']);


app.controller('Details', ['$scope', function($scope){
    var self = this;

    var videoFill = function(){
        var area = document.getElementById('player');
        area.style.height = (window.innerHeight - $('#player').offset().top) + 'px';
    };

    window.addEventListener('resize', function(){
        videoFill();
    });

    $scope.isPlaying = false;

    self.showPlayer = function(){
        $scope.isPlaying = true;

        var area = document.getElementById('player');

        videojs(area, {autoplay: true}, function(){
          videoFill();
        });
    }
}]);