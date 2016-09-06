(function() {
    'use strict';
    angular.module('taskApp', ['ngAnimate', 'vAccordion', 'ui.bootstrap'])
    .controller('taskAppController', ['$scope','$http', '$uibModal',
        function($scope, $http, $uibModal) {
            var getTasks = function(){
                $http({url: '/taskApp/api/task/top',
                      method: 'GET'})
                .then(function taskSuccess(response){
                        $scope.tasks = response.data.tasks;
                        $scope.totalWork = response.data.total_work;
                    }, function taskFail(response){
                        console.log(response);
                    });
            }
            getTasks();
        
            $scope.task = function(id, name, kind) {
                id = id || null;
                name = name || null;
                kind = kind || 'add';
                var modalInstance = $uibModal.open({
                    animation: true,
                    ariaLabelledBy: 'modal-title',
                    ariaDescribedBy: 'modal-body',
                    templateUrl: 'views/task_modal.html',
                    controller: 'ModalInstanceCtrl',
                    controllerAs: '$ctrl',
                    size: 'lg',
                    resolve: {
                      item: function () {
                        return {kind: kind,
                                id: id,
                                name: name
                                };
                      }
                    }
                });
                modalInstance.result.then(function (item) {
                    var e = item;
                }, function () {
                    console.log('canceled');
                });
            };
        }
        
    ])
    .controller('ModalInstanceCtrl',
    function ($uibModalInstance, item) {
        var $http = angular.injector(["ng"]).get("$http");
        var $ctrl = this;
        angular.forEach(item, function(value, key) {
            this[key] = value;
        }, $ctrl);
        console.log($ctrl);
        $http({url: '/taskApp/api/task/' + $ctrl.id,
            method: 'GET'})
        .then(function taskSuccess(response){
            console.log(response.data);
            angular.forEach(response.data.tasks[0], function(value, key) {
                this[key] = value;
            }, $ctrl);
            $ctrl.block = $ctrl.block.id || ''
            $ctrl.estimate = $ctrl.estimate / 60 + 'h';
        }, function taskFail(response){
            console.log(response);
        });
        
        $ctrl.title;
        $ctrl.$onInit = function () {
            console.log('init');
        };
        $ctrl.save = function (isValid) {
            if (!isValid) {
                return false;
            }
            console.log('ok in ctrl');
            $uibModalInstance.close(null);
            return true;
        };
      
        $ctrl.cancel = function () {
          console.log('cancel in ctrl');
          $uibModalInstance.dismiss('cancel');
        };
    });
}());
