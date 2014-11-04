;(function(global, factory) {
    if (typeof define === 'function' && define.amd) {
        define(['knockout', 'jquery', 'osfutils'], factory);
    } else {
        global.RevisionTable  = factory(ko, jQuery);
    }
}(this, function(ko, $) {

    'use strict';

    ko.punches.enableAll();
    ko.punches.attributeInterpolationMarkup.enable();

    var Revision = function(data) {

        var self = this;

        $.extend(self, data);
        self.date = new $.osf.FormattableDate(data.date);
        self.displayDate = self.date.local !== 'Invalid date' ?
            self.date.local :
            data.date;

    };

    var RevisionsViewModel = function(node, path, editable, urls) {

        var self = this;

        self.node = node;
        self.path = path;
        self.editable = editable;
        self.urls = urls;
        self.page = 0;
        self.more = ko.observable(false);
        self.revisions = ko.observableArray([]);

    };

    RevisionsViewModel.prototype.fetch = function() {
        var self = this;
        $.getJSON(
            self.urls.revisions,
            {page: self.page}
        ).done(function(response) {
            self.more(response.more);
            var revisions = ko.utils.arrayMap(response.revisions, function(item) {
                return new Revision(item);
            });
            self.revisions(self.revisions().concat(revisions));
            self.page += 1;
        });
    };

    RevisionsViewModel.prototype.delete = function() {
        var self = this;
        $.ajax({
            type: 'DELETE',
            url: self.urls.delete,
        }).done(function() {
            window.location = self.urls.files;
        }).fail(function() {
            bootbox.alert('Could not delete file.');
        });
    };

    RevisionsViewModel.prototype.askDelete = function() {
        var self = this;
        bootbox.confirm({
            title: 'Delete file?',
            message: 'Are you sure you want to delete <strong>' +
                self.path + '</strong>?',
            callback: function(confirm) {
                if (confirm) {
                    self.delete();
                }
            }
        });
    };

    var RevisionTable = function(selector, node, path, editable, urls) {

        var self = this;

        self.viewModel = new RevisionsViewModel(node, path, editable, urls);
        self.viewModel.fetch();
        $.osf.applyBindings(self.viewModel, selector);

    };

    return RevisionTable;

}));
