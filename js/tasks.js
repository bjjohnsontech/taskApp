(function() {
    'use strict';
    angular.module('taskApp', ['ngAnimate', 'vAccordion', 'ui.bootstrap'])
    .controller('taskAppController', ['$scope','$http', '$uibModal',
        function($scope, $http, $uibModal) {
            var getTasks = function(){
                $http({url: '/taskApp/api/task/',
                      method: 'GET'})
                .then(function taskSuccess(response){
                        $scope.tasks = response.data.tasks;
                        $scope.totalWork = response.data.total_work;
                    }, function taskFail(response){
                        console.log(response);
                    });
            }
            getTasks();
        
            $scope.newTask = function (id, name, kind) {
                id = id || null;
                name = name || null;
                kind = kind || 'Add';
                var modalInstance = $uibModal.open({
                    animation: true,
                    ariaLabelledBy: 'modal-title',
                    ariaDescribedBy: 'modal-body',
                    templateUrl: 'views/task_modal.html',
                    controller: 'ModalInstanceCtrl',
                    controllerAs: '$ctrl',
                    size: 'lg',
                    resolve: {
                      items: function () {
                        return [kind];
                      },
                      name: name,
                      id: id,
                    }
                });
                modalInstance.result.then(function (selectedItem) {
                    var e = selectedItem;
                }, function () {
                    console.log('canceled');
                });
            };
        }
        
    ])
    .controller('ModalInstanceCtrl', function ($uibModalInstance, items, name, id) {
        var $ctrl = this;
        $ctrl.kind = items[0];
        $ctrl.id = id;
        $ctrl.name = name;
        
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
