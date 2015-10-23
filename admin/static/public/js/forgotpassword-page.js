webpackJsonp([16],{

/***/ 0:
/***/ function(module, exports, __webpack_require__) {

/**
 * Forgot Password page
 */

var forgotPassword = __webpack_require__(354);

new forgotPassword.ForgotPassword('#forgotPasswordForm');


/***/ },

/***/ 150:
/***/ function(module, exports, __webpack_require__) {

/*
 * Maintains the base class for knockoutJS form ViewModels
 */
'use strict';

var ko = __webpack_require__(48);

var $osf = __webpack_require__(47);
var oop = __webpack_require__(146);

var ValidationError = oop.extend(Error, {
    constructor: function (messages, header, level) {
        this.super.constructor.call(this);
        this.messages = messages || [];
        this.header = header || 'Error';
        this.level = level || 'warning';
    }
});

/**
* Base class KO viewmodel based forms should inherit from.
*
* Note: isValid needs to be implemented by subclasses and onError can
* optionally be implemented by subclasses to handle ValidationError(s) as desired.
*/
var FormViewModel = oop.defclass({
    constructor: function() {},
    isValid: function() {
        throw new Error('FormViewModel subclass must implement isValid');
    },
    onError: function(validationError) {
        for (var i = 0; i < validationError.messages.length; i++) {
            $osf.growl(
                validationError.header,
                validationError.messages[i],
                validationError.level
            );
        }
    },
    submit: function() {
        try {
            this.isValid();
            return true; // Allow form to submit normally
        } catch (err) {
            if (err instanceof ValidationError) {
                this.onError(err);
                return false; // Stop form submission
            } else {
                throw err;
            }
        }
    }
});


module.exports = {
    FormViewModel: FormViewModel,
    ValidationError: ValidationError
};

/***/ },

/***/ 354:
/***/ function(module, exports, __webpack_require__) {

/*
 * forgot password view model
 */
'use strict';

var ko = __webpack_require__(48);
__webpack_require__(143);

var $osf = __webpack_require__(47);
var oop = __webpack_require__(146);
var formViewModel = __webpack_require__(150);

var ForgotPasswordViewModel = oop.extend(formViewModel.FormViewModel, {
    constructor: function() {
        var self = this;
        self.super.constructor.call(self);
        self.username = ko.observable('').extend({
            required: true,
            email: true
        });
    },
    isValid: function() {
        var validationError = new formViewModel.ValidationError();
        if (!this.username.isValid()) {
            validationError.messages.push('Please enter a valid email address.');
            throw validationError;
        } else {
            return true;
        }
    }
});


var ForgotPassword = function(selector) {
    this.viewModel = new ForgotPasswordViewModel();
    $osf.applyBindings(this.viewModel, selector);
};

module.exports = {
    ForgotPassword: ForgotPassword,
    ViewModel: ForgotPasswordViewModel
};


/***/ }

});
//# sourceMappingURL=forgotpassword-page.js.map