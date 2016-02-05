var app = angular.module('rlscloud.rls.latest', ['rlscloud']);

app.directive('thumbnail', ['$interval', function($interval){
    var SPEED = 500;

    return {
        restrict: 'E',
        scope: {
            url: '@'
        },
        link: function(scope, elem, attrs){
            var imageElem = $('.image', elem);
            imageElem.css({
                width: attrs.width + 'px',
                height: attrs.height + 'px',
                backgroundImage: "url('" + attrs.image + "')"
            });

            // Thumbnail spinner -----------------------------------------------
            var spinner;
            var stripPosition = 0;
            var frameWidth = parseInt(attrs.width);
            var stripWidth = frameWidth * parseInt(attrs.frames);

            function spinOnce(){
                stripPosition = (stripPosition + frameWidth) % stripWidth;
                    imageElem.css({backgroundPositionX: '-' + stripPosition + 'px'});
            }

            scope.startSpin = function(){
                spinOnce();
                spinner = $interval(spinOnce, SPEED);
            };

            scope.stopSpin = function(){
                $interval.cancel(spinner);
            }
        },
        template: '<a ng-href="[[ url ]]" ng-mouseenter="startSpin()" ng-mouseleave="stopSpin()"><div class="image"></div></a>'
    }
}]);