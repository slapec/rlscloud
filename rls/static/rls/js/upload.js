var app = angular.module('rlscloud.rls.upload', ['rlscloud']);

app.filter('iconClass', function(){
    var states = {
        waiting: 'clock-o',
        uploading: 'cloud-upload',
        uploaded: 'check',
        error: 'exclamation',
        canceled: 'times'
    };

    return function(stateCode){
        return states[stateCode];
    }
});

app.filter('colorClass', function(){
    var states = {
        waiting: '',
        uploading: 'bg-info',
        uploaded: 'bg-success',
        error: 'bg-danger',
        canceled: 'bg-warning'
    };

    return function(stateCode){
        return states[stateCode]
    }
});

app.controller('Upload', ['$scope', 'options', 'urls', function($scope, options, urls){
    var self = this;

    // File object handling ----------------------------------------------------
    $scope.dragActive = false;
    $scope.files = [];

    $(document).on('dragover', function(e){
        e.stopPropagation();
        e.preventDefault();
        e.originalEvent.dataTransfer.dropEffect = 'copy';

        $scope.$apply(function(){
            $scope.dragActive = true;
        });
    });

    $(document).on('drop', function(e){
        e.stopPropagation();
        e.preventDefault();

        $scope.$apply(function(){
            $scope.dragActive = false;

            angular.forEach(e.originalEvent.dataTransfer.files, function(o){
                o.$progress = 0;
                o.$state = 'waiting';
                $scope.files.push(o);
            });
        });
    });

    $(document).on('dragend', function(e){
        $scope.$apply(function(){
            $scope.dragActive = false;
        });
    });

    // Uploader ----------------------------------------------------------------
    var uploadApi = urls.upload;
    var uploadInProgress = false;

    var uploadNextFile = function(){
        if(uploadInProgress){
            return;
        }

        var nextFile = null;
        for(var i=0; i<$scope.files.length; i++){
            if($scope.files[i].$state === 'waiting'){
                nextFile = $scope.files[i];
                break;
            }
        }

        if(nextFile){
            uploadInProgress = true;

            var form = new FormData();
            form.append('file', nextFile);
            form.append('csrfmiddlewaretoken', options.csrf_token);

            $.ajax({
                url: uploadApi,
                type: 'POST',
                data: form,
                processData: false,
                contentType: false,
                xhr: function(){
                    var xhr = $.ajaxSettings.xhr();
                    nextFile.xhr = xhr;

                    xhr.upload.onloadstart = function(e){
                        nextFile.$start = new Date();
                    };

                    xhr.upload.onprogress = function(e){
                        $scope.$applyAsync(function(){
                            nextFile.$progress = (e.loaded / e.total) * 100;
                            nextFile.$speed = e.loaded / ((new Date() - nextFile.$start) / 1000);
                            nextFile.$state = 'uploading';
                        })
                    };

                    xhr.upload.onerror = function(e){
                        $scope.$applyAsync(function(){
                            nextFile.$state = 'error';
                        });
                        uploadInProgress = false;
                        uploadNextFile();
                    };

                    xhr.upload.onabort = function(e){
                        uploadInProgress = false;
                        uploadNextFile();
                    };

                    xhr.upload.onload = function(e){
                        $scope.$applyAsync(function(){
                            nextFile.$state = 'uploaded';
                        });
                        uploadInProgress = false;
                        uploadNextFile();
                    };

                    return xhr;
                }
            })
        }
    };

    $scope.$watchCollection('files', function(new_, old){
        if(new_.length > 0){
            uploadNextFile();
        }
    });

    self.cancel = function(file){
        file.$state = 'canceled';
        try {
            file.xhr.abort();
        }
        catch(TypeError){}
        $scope.$applyAsync(function(){
            file.$state = 'canceled';
        });
    };

    self.remove = function(file){
        $scope.$applyAsync(function(){
            $scope.files.splice($scope.files.indexOf(file), 1);
        });
    };
}]);

app.directive('model', [function(){
    return {
        scope: {
            model: '='
        },
        link: function(scope, element){
            element.change(function(){
                var self = this;

                scope.$apply(function(){
                    angular.forEach(self.files, function(o){
                        o.$progress = 0;
                        o.$state = 'waiting';
                        scope.model.push(o);
                    });
                });
            });
        }
    }
}]);