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
            };
            getTasks();
        
            $scope.task = function(task, kind) {
                task = task || null;
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
                                task: task
                                };
                      }
                    }
                });
                modalInstance.result.then(function (item) {
                    if (kind == 'Edit'){
                        task = item;
                    } else if (task) {
                        task.children.push(item);
                    } else {
                        $scope.tasks.push(item);
                    }
                }, function () {
                    console.log('canceled');
                });
            };
            $scope.recordWork = function(pane) {
                console.log(pane);
            };
            
            $scope.startRecord = function(pane) {
                $http({url: '/taskApp/api/work/',
                    type: 'application/json',
                    method: 'POST',
                    data: {task: pane.id, start_time: new Date()}
                })
                .then(function taskSuccess(response){
                    //console.log(response.data);
                    pane.work.push(response.data);
                }, function taskFail(response){
                    console.log(response);
                });
            };
            
            $scope.endRecord = function(work) {
                $http({url: '/taskApp/api/work/' + work.id,
                    type: 'application/json',
                    method: 'PUT',
                    data: {id: work.id, end_time: new Date()}
                })
                .then(function taskSuccess(response){
                    work.end_time = response.data.end_time;
                }, function taskFail(response){
                    console.log(response);
                });
            };
        }
        
    ])
    .controller('ModalInstanceCtrl',
    function ($uibModalInstance, item) {
        var $http = angular.injector(["ng"]).get("$http");
        var $ctrl = this;
        var method = 'POST';
        var url = '/taskApp/api/task/';
        $ctrl.task = {name:'', description: '', parent: '', completed: '',
                      block: '', label: '', assigned: '', estimate: ''};
        $ctrl.kind = item.kind;
        // if edit, set ctrl.task to the passed value
        if ($ctrl.kind == 'edit') {
            angular.forEach(item.task, function(value, key) {
                this.task[key] = value;
            }, $ctrl);
            $ctrl.task.block = $ctrl.block.id || '';
            $ctrl.task.estimate = $ctrl.estimate / 60 + 'h' || '';
            url += $ctrl.id;
            method = 'PUT';
        } else if (item.task) {
            // else, passed task is parent, set parent id
            $ctrl.task.parent = item.task.id;
        }
        $ctrl.$onInit = function () {
            console.log('init');
        };
        $ctrl.save = function (isValid) {
            if (!isValid) {
                return false;
            }
            $http({url: url,
                type: 'application/json',
                method: method,
                data: $ctrl.task})
            .then(function taskSuccess(response){
                //console.log(response.data);
                $ctrl.task = response.data;
            }, function taskFail(response){
                console.log(response);
            });
            $uibModalInstance.close($ctrl.task);
            return true;
        };
        $ctrl.cancel = function () {
          console.log('cancel in ctrl');
          $uibModalInstance.dismiss('cancel');
        };
    });
}());
